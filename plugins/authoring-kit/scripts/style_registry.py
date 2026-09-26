#!/usr/bin/env python3
"""문체 설정 레지스트리 — 전역 설정을 voice 가 계승·확장한다.

문체 설정은 두 갈래다.

    정량  어휘 목록(lexicon)   항목마다 채택 가중치(-3~+3)와 필터(enabled). 기계가 센다.
    정성  지시 목록(directives) 모델에게 들어가는 지시문. 게이트에 붙으면 **읽고 판단만** 한다.

세 벌이 겹쳐 유효값이 된다. 뒤가 앞을 덮는다.

    ① 플러그인 기본값   skills/authoring-method/assets/style/   읽기 전용. 분류 체계와 기본 어휘
    ② 전역 설정         ~/.claude/authoring/global/style.json   모든 voice 가 계승한다
    ③ voice 설정        ~/.claude/authoring/voices/<id>/style.json

②·③ 은 **차분만** 저장한다(`overrides` · `add`). 기본값을 통째로 복사해 두면 플러그인이
분류 체계를 고쳐도 사용자 파일이 옛 판본으로 굳는다 — 그게 이 키트가 고치려던 복제 문제다.

갈래 소유권은 그대로 지킨다.

- 문체 설정 전체는 **L1 소유 축**(`register`·`rhythm`·`device`·`lexicon`)만 쓴다.
  정성 분류의 모든 범주가 넷 중 하나에 묶여 있고, 그렇지 않으면 `validate` 가 막는다.
- 어휘 항목 중 **L0 에서 온 것**(`l0` 필드)은 면제 규칙을 따른다.
  hard floor 축(`grammar` 등)에서 온 항목은 가중치를 올리거나 끌 수 없다.
  `machine-rhythm` 에서 온 항목을 끄거나 양수로 올리면 **그 항목에 대한 면제**라서 `reason` 이 필요하다.

표준 라이브러리만 쓴다. `authoring.py` 를 import 하지 않는다 — 스캐너가 이 모듈을 쓰는데,
스캐너는 레지스트리 없이도 돌아야 한다.
"""
from __future__ import annotations

import copy
import json
import os
import re
from pathlib import Path

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))
STYLE_ASSETS = PLUGIN_ROOT / "skills" / "authoring-method" / "assets" / "style"
LEXICON_CATALOG = STYLE_ASSETS / "lexicon.json"
QUALITATIVE_TAXONOMY = STYLE_ASSETS / "qualitative.json"

SCHEMA = "authoring-kit/style@1"

# authoring.py 와 같은 값이어야 한다 — fixtures/test_style.py 가 대조한다.
L1_AXES = ("register", "rhythm", "device", "lexicon")
HARD_FLOOR = {"evidence", "grammar", "comprehension"}
WAIVABLE = {"machine-rhythm"}

WEIGHT_MIN, WEIGHT_MAX = -3, 3

# 가중치 눈금. **0 이 '보통'이다** — 양수는 보통보다 적극, 음수는 보통보다 소극.
# `per_1000`·`min` 은 음수 대역의 허용량이다: 산문 1,000자당 몇 회까지, 단 최소 몇 회까지는 봐준다.
WEIGHT_BANDS: dict[int, dict] = {
    -3: {"name": "금지", "directive": "쓰지 않는다.", "per_1000": 0.0, "min": 0},
    -2: {"name": "강한 절제", "directive": "꼭 필요한 자리에서만, 글 전체에서 한두 번.", "per_1000": 0.5, "min": 1},
    -1: {"name": "절제", "directive": "대안이 있으면 대안을 쓴다.", "per_1000": 1.5, "min": 2},
    0: {"name": "보통", "directive": "", "per_1000": None, "min": None},
    1: {"name": "선호", "directive": "같은 뜻이면 이쪽을 고른다.", "per_1000": None, "min": None},
    2: {"name": "적극", "directive": "자리가 오면 쓴다.", "per_1000": None, "min": None},
    3: {"name": "표지", "directive": "이 목소리의 표지다. 자리가 오면 반드시 쓴다.", "per_1000": None, "min": None},
}

GATE_LEVELS = ("MUST", "SHOULD")
CHECK_MODES = ("count", "sentence-initial", "sentence-final", "paragraph-initial")
# 층에서 덮을 수 있는 분류 점검 값. 전부 **설계 초기값**이다(연구 노트 §2.1) — 코퍼스로 검증된 수치가 아니다.
CHECK_TUNABLE = ("density_per_1000", "stack")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9.-]*[a-z0-9]$")


# ── 위치 ─────────────────────────────────────────────────────────────────
def registry_home() -> Path:
    override = os.environ.get("AUTHORING_KIT_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".claude" / "authoring"


def global_path() -> Path:
    return registry_home() / "global" / "style.json"


def voice_path(voice_id: str) -> Path:
    return registry_home() / "voices" / voice_id / "style.json"


def layer_path(scope: str) -> Path:
    """scope: `global` 또는 `voice:<id>`."""
    if scope == "global":
        return global_path()
    if scope.startswith("voice:"):
        vid = scope.split(":", 1)[1]
        if not ID_RE.match(vid) and not re.match(r"^[a-z0-9]$", vid):
            raise ValueError(f"voice id 형식이 아니다: {vid!r}")
        return voice_path(vid)
    raise ValueError(f"알 수 없는 scope: {scope!r} (global | voice:<id>)")


# ── 로드 ─────────────────────────────────────────────────────────────────
def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def load_catalog() -> dict:
    return _read_json(LEXICON_CATALOG)


def load_taxonomy() -> dict:
    return _read_json(QUALITATIVE_TAXONOMY)


def empty_layer() -> dict:
    return {
        "$schema": SCHEMA,
        "schema_version": 1,
        "lexicon": {"overrides": {}, "categories": {}, "add": []},
        "directives": {"overrides": {}, "add": [], "choices": {}},
    }


def load_layer(scope: str) -> dict:
    p = layer_path(scope)
    if not p.exists():
        return empty_layer()
    raw = _read_json(p)
    base = empty_layer()
    for group in ("lexicon", "directives"):
        for k, v in (raw.get(group) or {}).items():
            base[group][k] = v
    for k, v in raw.items():
        if k not in ("lexicon", "directives"):
            base[k] = v
    return base


def save_layer(scope: str, layer: dict) -> Path:
    """검증을 통과한 레이어만 저장한다. 원자적으로 쓴다 — 편집기가 쓰다 죽어도 반쪽 파일이 남지 않게."""
    p = layer_path(scope)
    p.parent.mkdir(parents=True, exist_ok=True)
    clean = prune_layer(layer)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(clean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, p)
    return p


def prune_layer(layer: dict) -> dict:
    """빈 차분을 걷어낸다. 저장 파일이 '바꾼 것'만 보여야 사람이 읽고 리뷰할 수 있다."""
    out = {"$schema": SCHEMA, "schema_version": 1}
    for k, v in layer.items():
        if k in ("$schema", "schema_version", "lexicon", "directives"):
            continue
        out[k] = v
    lex = layer.get("lexicon", {})
    overrides = {k: {f: x for f, x in v.items() if x is not None and x != ""}
                 for k, v in (lex.get("overrides") or {}).items()}
    overrides = {k: v for k, v in overrides.items() if v}
    cats = {k: v for k, v in (lex.get("categories") or {}).items() if v}
    out["lexicon"] = {"overrides": dict(sorted(overrides.items())),
                      "categories": dict(sorted(cats.items())),
                      "add": list(lex.get("add") or [])}
    d = layer.get("directives", {})
    d_over = {k: v for k, v in (d.get("overrides") or {}).items() if v}
    out["directives"] = {"overrides": dict(sorted(d_over.items())), "add": list(d.get("add") or [])}
    # 고른 선택지 — 분류 id → 선택지 id 목록. 빈 목록도 남긴다: voice 에서 "이 분류는 아무것도 고르지 않음"이다.
    ch = {k: list(v) for k, v in (d.get("choices") or {}).items() if isinstance(v, list)}
    if ch:
        out["directives"]["choices"] = dict(sorted(ch.items()))
    return out


def voice_exists(voice_id: str) -> bool:
    return (registry_home() / "voices" / voice_id / "voice.json").exists()


def list_voices() -> list[dict]:
    d = registry_home() / "voices"
    out = []
    if d.is_dir():
        for p in sorted(d.glob("*/voice.json")):
            try:
                v = _read_json(p)
            except Exception:
                continue
            out.append({"id": p.parent.name, "label": v.get("label", ""),
                        "status": v.get("status"), "usage": v.get("usage"),
                        "has_style": (p.parent / "style.json").exists()})
    return out


# ── 병합 ─────────────────────────────────────────────────────────────────
def _category_index(catalog: dict) -> dict[str, dict]:
    return {c["id"]: c for c in catalog.get("categories", [])}


def _category_chain(cat_id: str, cats: dict[str, dict]) -> list[dict]:
    chain, seen = [], set()
    cur = cats.get(cat_id)
    while cur and cur["id"] not in seen:
        chain.append(cur)
        seen.add(cur["id"])
        cur = cats.get(cur.get("parent")) if cur.get("parent") else None
    return list(reversed(chain))


def category_setting(cat_id: str, cats: dict[str, dict], key: str, default=None):
    """카테고리 설정은 부모에서 물려받는다(가장 가까운 조상의 값)."""
    for c in reversed(_category_chain(cat_id, cats)):
        if key in c.get("check", {}):
            return c["check"][key]
    return default


def _norm_item(it: dict, source: str, cats: dict[str, dict]) -> dict:
    x = copy.deepcopy(it)
    x.setdefault("forms", [])
    x.setdefault("functions", [])
    x.setdefault("alternatives", [])
    x.setdefault("enabled", True)
    x.setdefault("weight", 0)
    x.setdefault("note", "")
    x["source"] = source
    x["weight_from"] = source
    x["enabled_from"] = source
    x["base_weight"] = x["weight"]
    x["base_enabled"] = x["enabled"]
    x["reason"] = x.get("reason", "")
    x["mode"] = x.get("mode") or category_setting(x.get("category", ""), cats, "mode", "count")
    x["boundary"] = x.get("boundary") or category_setting(x.get("category", ""), cats, "boundary", "word")
    return x


def _apply_item_override(x: dict, ov: dict, source: str) -> None:
    if "weight" in ov and ov["weight"] is not None:
        x["weight"] = ov["weight"]
        x["weight_from"] = source
    if "enabled" in ov and ov["enabled"] is not None:
        x["enabled"] = ov["enabled"]
        x["enabled_from"] = source
    if ov.get("reason"):
        x["reason"] = ov["reason"]
    if ov.get("alternatives"):
        x["alternatives"] = ov["alternatives"]
    if ov.get("note"):
        x["note"] = ov["note"]


def effective(voice_id: str | None = None, *, layers: dict | None = None) -> dict:
    """유효 문체 설정. voice_id 가 None 이면 전역까지만 적용한다.

    layers 로 레이어를 직접 넘기면 디스크를 읽지 않는다 — 편집기가 저장 전 미리보기에 쓴다.
    반환값의 각 항목은 **어디서 왔는지**(source · weight_from · enabled_from)를 달고 있다.
    편집기가 '상속'과 '재정의'를 보여 줘야 사용자가 무엇을 바꿨는지 안다.
    """
    catalog = load_catalog()
    taxonomy = load_taxonomy()
    cats = _category_index(catalog)
    layers = layers or {}
    g = layers.get("global") if "global" in layers else load_layer("global")
    v = None
    if voice_id:
        key = f"voice:{voice_id}"
        v = layers.get(key) if key in layers else load_layer(key)

    items: dict[str, dict] = {}
    for it in catalog.get("items", []):
        items[it["id"]] = _norm_item(it, "default", cats)

    cat_state = {cid: {"enabled": True, "enabled_from": "default"} for cid in cats}
    stack = [("global", g)] + ([("voice", v)] if v is not None else [])
    for source, layer in stack:
        lex = layer.get("lexicon", {})
        for it in lex.get("add") or []:
            if it.get("id") and it["id"] not in items:
                items[it["id"]] = _norm_item(it, source, cats)
        for iid, ov in (lex.get("overrides") or {}).items():
            if iid in items:
                _apply_item_override(items[iid], ov, source)
        for cid, ov in (lex.get("categories") or {}).items():
            if cid not in cat_state:
                continue
            if "enabled" in ov and ov["enabled"] is not None:
                cat_state[cid].update({"enabled": bool(ov["enabled"]), "enabled_from": source})
            # 점검 기준값(밀도·겹침)은 설계 초기값이라 사용자가 조정한다. 키 단위로 덮는다.
            for k, x in (ov.get("check") or {}).items():
                if k in CHECK_TUNABLE:
                    cat_state[cid].setdefault("check", {})[k] = x
                    cat_state[cid].setdefault("check_from", {})[k] = source

    # 카테고리 필터는 아래로 전파된다 — 부모를 끄면 자식도 꺼진다.
    def cat_on(cid: str) -> bool:
        return all(cat_state.get(c["id"], {}).get("enabled", True) for c in _category_chain(cid, cats))

    for x in items.values():
        x["category_enabled"] = cat_on(x.get("category", ""))
        x["active"] = bool(x["enabled"]) and x["category_enabled"]

    # 정성 지시
    tcats = {c["id"]: c for c in taxonomy.get("categories", [])}
    directives: dict[str, dict] = {}
    for source, layer in stack:
        d = layer.get("directives", {})
        for di in d.get("add") or []:
            if not di.get("id") or di["id"] in directives:
                continue
            x = copy.deepcopy(di)
            x.setdefault("enabled", True)
            x.setdefault("gate", {"enabled": False, "level": "SHOULD"})
            x["gate"].setdefault("level", "SHOULD")
            x["gate"].setdefault("enabled", False)
            x["source"] = source
            x["overridden_by"] = None
            x["axis"] = tcats.get(x.get("category", ""), {}).get("axis")
            directives[x["id"]] = x
        for did, ov in (d.get("overrides") or {}).items():
            if did not in directives:
                continue
            x = directives[did]
            for k in ("enabled", "text", "example"):
                if k in ov and ov[k] is not None:
                    x[k] = ov[k]
            if isinstance(ov.get("gate"), dict):
                x["gate"] = {**x["gate"], **ov["gate"]}
            x["overridden_by"] = source

    # 고른 선택지 — 분류 단위로 위 층이 아래 층을 통째로 대신한다(빈 목록 = 이 층에서는 고르지 않음).
    choices: dict[str, dict] = {}
    for source, layer in stack:
        for cid, ids in ((layer.get("directives", {}) or {}).get("choices") or {}).items():
            if isinstance(ids, list):
                choices[cid] = {"ids": list(ids), "source": source,
                                "overrides": choices.get(cid, {}).get("source")}
    for cid, ch in choices.items():
        cat = tcats.get(cid) or {}
        opts = {o["id"]: o for o in cat.get("options") or []}
        for oid in ch["ids"]:
            o = opts.get(oid)
            if not o:
                continue  # 검증이 막는다. 여기서는 모르는 선택지를 싣지 않을 뿐이다
            did = f"{cid}#{oid}"
            directives[did] = {"id": did, "category": cid, "text": o["text"], "enabled": True,
                               "gate": {"enabled": False, "level": "SHOULD"}, "source": ch["source"],
                               "overridden_by": None, "axis": cat.get("axis"),
                               "choice": {"option": oid, "group": o.get("group")}}

    out_cats = []
    for c in catalog.get("categories", []):
        st = cat_state.get(c["id"], {})
        merged = {**c, **{k: v for k, v in st.items() if k != "check"}, "active": cat_on(c["id"])}
        merged["check"] = {**(c.get("check") or {}), **(st.get("check") or {})}
        merged["base_check"] = c.get("check") or {}
        out_cats.append(merged)

    return {
        "voice": voice_id,
        # 카탈로그 순서를 지킨다 — L0 스캐너가 목록 순서대로 첫 일치를 고르는 자리가 있다(H2).
        "items": list(items.values()),
        "categories": out_cats,
        "directives": list(directives.values()),
        # 분류마다 고른 선택지와 그 출처. 편집기가 체크 상태·계승·재정의를 그린다.
        "choices": choices,
    }


# ── 검증 ─────────────────────────────────────────────────────────────────
def _check_regex(rx: str | None, where: str, problems: list[str]) -> None:
    if not rx:
        return
    try:
        re.compile(rx)
    except re.error as e:
        problems.append(f"{where}: 정규식이 깨졌다 — {e}")


def validate_layer(scope: str, layer: dict, *, base_layers: dict | None = None) -> list[str]:
    """레이어 하나를 검증한다. 문제 목록이 비면 통과다.

    **조용히 고쳐 저장하지 않는다.** 잘못된 값은 사용자에게 되돌려 보내고 저장을 거부한다.
    """
    problems: list[str] = []
    catalog = load_catalog()
    taxonomy = load_taxonomy()
    cats = _category_index(catalog)
    tcats = {c["id"]: c for c in taxonomy.get("categories", [])}
    where = scope

    # 이 레이어 **아래** 층까지의 유효 항목 — override 대상과 L0 기원을 판정하는 기준.
    below: dict = {"global": empty_layer()} if scope == "global" else {}
    if base_layers:
        below.update(base_layers)
    base = effective(None, layers=below)
    base_items = {x["id"]: x for x in base["items"]}
    base_dirs = {x["id"]: x for x in base["directives"]}

    lex = layer.get("lexicon", {}) or {}
    added_ids: set[str] = set()
    for it in lex.get("add") or []:
        iid = it.get("id", "")
        w = f"{where}/lexicon.add[{iid or '?'}]"
        if not ID_RE.match(iid or ""):
            problems.append(f"{w}: id 는 소문자·숫자·점·하이픈만 쓴다")
        if iid in base_items or iid in added_ids:
            problems.append(f"{w}: 이미 있는 id 다. 기존 항목을 바꾸려면 overrides 를 쓴다")
        added_ids.add(iid)
        if it.get("category") not in cats:
            problems.append(f"{w}: 알 수 없는 분류 '{it.get('category')}'")
        if not it.get("forms") and not it.get("regex"):
            problems.append(f"{w}: forms 나 regex 중 하나는 있어야 한다 — 셀 대상이 없다")
        if it.get("l0"):
            problems.append(f"{w}: l0 기원은 플러그인 기본값만 가진다. 사용자 항목은 L1 이다")
        _check_regex(it.get("regex"), w, problems)
        _check_regex(it.get("except"), w, problems)
        _check_weight(it.get("weight", 0), w, problems)
        if it.get("mode") and it["mode"] not in CHECK_MODES:
            problems.append(f"{w}: mode 는 {CHECK_MODES} 중 하나")
        for f in it.get("functions", []):
            if f not in {x["id"] for x in catalog.get("functions", [])}:
                problems.append(f"{w}: 알 수 없는 기능 태그 '{f}'")

    for iid, ov in (lex.get("overrides") or {}).items():
        w = f"{where}/lexicon.overrides[{iid}]"
        target = base_items.get(iid)
        if target is None:
            problems.append(f"{w}: 덮을 항목이 아래 층에 없다")
            continue
        if "weight" in ov and ov["weight"] is not None:
            _check_weight(ov["weight"], w, problems)
        l0 = target.get("l0") or {}
        axis = l0.get("axis")
        new_w = ov.get("weight", target["weight"])
        new_w = target["weight"] if new_w is None else new_w
        new_on = ov.get("enabled", target["enabled"])
        new_on = target["enabled"] if new_on is None else new_on
        if axis in HARD_FLOOR:
            if isinstance(new_w, (int, float)) and new_w > target["base_weight"]:
                problems.append(f"{w}: hard floor({axis}) 항목의 가중치를 올릴 수 없다 "
                                f"({target['base_weight']} → {new_w}). 어떤 설정도 이 층을 면제하지 못한다")
            if new_on is False:
                problems.append(f"{w}: hard floor({axis}) 항목은 끌 수 없다")
        elif axis in WAIVABLE:
            waives = (new_on is False) or (isinstance(new_w, (int, float)) and new_w > 0)
            if waives and not (ov.get("reason") or target.get("reason")):
                problems.append(f"{w}: L0 {l0.get('code')} 항목을 끄거나 양수로 올리는 것은 면제다 — "
                                f"reason 이 없으면 거부된다. 조용한 면제는 만들지 않는다")

    for cid, ov in (lex.get("categories") or {}).items():
        if cid not in cats:
            problems.append(f"{where}/lexicon.categories[{cid}]: 알 수 없는 분류")
            continue
        for k, x in (ov.get("check") or {}).items():
            if k not in CHECK_TUNABLE:
                problems.append(f"{where}/lexicon.categories[{cid}].check: '{k}' 는 덮을 수 없다 ({CHECK_TUNABLE})")
            elif x is not None and (isinstance(x, bool) or not isinstance(x, (int, float)) or x <= 0
                                    or (k == "stack" and not float(x).is_integer())):
                problems.append(f"{where}/lexicon.categories[{cid}].check.{k}: 양수여야 한다"
                                + (" (정수)" if k == "stack" else "") + f" — 받은 값 {x!r}")
        if ov.get("enabled") is False:
            floor = [x["id"] for x in base_items.values()
                     if (x.get("l0") or {}).get("axis") in HARD_FLOOR
                     and any(c["id"] == cid for c in _category_chain(x.get("category", ""), cats))]
            if floor:
                problems.append(f"{where}/lexicon.categories[{cid}]: hard floor 항목이 든 분류는 끌 수 없다 "
                                f"({', '.join(floor[:4])}{'…' if len(floor) > 4 else ''})")

    d = layer.get("directives", {}) or {}
    seen: set[str] = set()
    for di in d.get("add") or []:
        did = di.get("id", "")
        w = f"{where}/directives.add[{did or '?'}]"
        if not ID_RE.match(did or ""):
            problems.append(f"{w}: id 는 소문자·숫자·점·하이픈만 쓴다")
        if did in base_dirs or did in seen:
            problems.append(f"{w}: 이미 있는 지시 id 다. 바꾸려면 overrides 를 쓴다")
        seen.add(did)
        cat = tcats.get(di.get("category"))
        if not cat:
            problems.append(f"{w}: 알 수 없는 정성 분류 '{di.get('category')}'")
        elif cat.get("axis") not in L1_AXES:
            problems.append(f"{w}: 갈래 위반 — 분류 '{cat['id']}' 의 축 '{cat.get('axis')}' 는 L1 소유가 아니다")
        if not (di.get("text") or "").strip():
            problems.append(f"{w}: 지시문(text)이 비었다")
        _check_gate(di.get("gate"), w, problems)
    ch = d.get("choices") or {}
    if not isinstance(ch, dict):
        problems.append(f"{where}/directives.choices: {{분류 id: [선택지 id…]}} 객체다")
        ch = {}
    for cid, ids in ch.items():
        w = f"{where}/directives.choices[{cid}]"
        cat = tcats.get(cid)
        if not cat or not cat.get("parent"):
            problems.append(f"{w}: 알 수 없는 정성 분류 — 선택지는 하위 분류(예: tenor.formality)에 고른다")
            continue
        if not isinstance(ids, list) or not all(isinstance(x, str) for x in ids):
            problems.append(f"{w}: 선택지 id 의 목록이어야 한다")
            continue
        opts = {o["id"]: o for o in cat.get("options") or []}
        unknown = [x for x in ids if x not in opts]
        if unknown:
            problems.append(f"{w}: 없는 선택지 {unknown} — 이 분류의 선택지는 {list(opts)}")
        if len(set(ids)) != len(ids):
            problems.append(f"{w}: 같은 선택지를 두 번 골랐다")
        spec = [x for x in ids if opts.get(x, {}).get("group") == "spectrum"]
        if len(spec) > 1:
            problems.append(f"{w}: 스펙트럼 선택지는 하나만 고른다 — {spec} "
                            f"(한 분류를 두 방향으로 동시에 맞출 수 없다)")
    for did, ov in (d.get("overrides") or {}).items():
        w = f"{where}/directives.overrides[{did}]"
        if did not in base_dirs:
            problems.append(f"{w}: 덮을 지시가 아래 층에 없다")
            continue
        if "text" in ov and not (ov["text"] or "").strip():
            problems.append(f"{w}: 지시문을 빈 값으로 덮을 수 없다 — 끄려면 enabled=false")
        if "gate" in ov:
            _check_gate({**base_dirs[did].get("gate", {}), **(ov["gate"] or {})}, w, problems)
    return problems


def _check_weight(wt, where: str, problems: list[str]) -> None:
    if not isinstance(wt, int) or isinstance(wt, bool) or not (WEIGHT_MIN <= wt <= WEIGHT_MAX):
        problems.append(f"{where}: weight 는 {WEIGHT_MIN}~{WEIGHT_MAX} 정수다 (받은 값 {wt!r})")


def _check_gate(g, where: str, problems: list[str]) -> None:
    if g is None:
        return
    if not isinstance(g, dict):
        problems.append(f"{where}: gate 는 {{enabled, level}} 객체다")
        return
    if g.get("level", "SHOULD") not in GATE_LEVELS:
        problems.append(f"{where}: gate.level 은 {GATE_LEVELS} 중 하나")


def validate_catalog() -> list[str]:
    """플러그인 기본값 자체의 정합. 회귀 검사가 돌린다."""
    problems: list[str] = []
    catalog, taxonomy = load_catalog(), load_taxonomy()
    cats = _category_index(catalog)
    fn_ids = {f["id"] for f in catalog.get("functions", [])}
    for c in catalog.get("categories", []):
        if c.get("parent") and c["parent"] not in cats:
            problems.append(f"catalog/category[{c['id']}]: 부모 '{c['parent']}' 가 없다")
        mode = c.get("check", {}).get("mode")
        if mode and mode not in CHECK_MODES:
            problems.append(f"catalog/category[{c['id']}]: mode '{mode}'")
    seen = set()
    for it in catalog.get("items", []):
        w = f"catalog/item[{it.get('id')}]"
        if it["id"] in seen:
            problems.append(f"{w}: id 중복")
        seen.add(it["id"])
        if not ID_RE.match(it["id"]):
            problems.append(f"{w}: id 형식")
        if it.get("category") not in cats:
            problems.append(f"{w}: 분류 '{it.get('category')}' 가 없다")
        if not it.get("forms") and not it.get("regex"):
            problems.append(f"{w}: 셀 대상이 없다")
        for f in it.get("functions", []):
            if f not in fn_ids:
                problems.append(f"{w}: 기능 태그 '{f}' 가 없다")
        _check_regex(it.get("regex"), w, problems)
        _check_regex(it.get("except"), w, problems)
        _check_weight(it.get("weight", 0), w, problems)
        l0 = it.get("l0")
        if l0 and l0.get("axis") not in HARD_FLOOR | WAIVABLE:
            problems.append(f"{w}: l0.axis '{l0.get('axis')}' 는 L0 축이 아니다")
    for c in taxonomy.get("categories", []):
        if c.get("parent") is None and not c.get("axis"):
            continue
        if c.get("axis") and c["axis"] not in L1_AXES:
            problems.append(f"taxonomy/category[{c['id']}]: 축 '{c['axis']}' 는 L1 소유가 아니다")
        opts = c.get("options") or []
        if c.get("parent") and not opts:
            problems.append(f"taxonomy/category[{c['id']}]: 고를 수 있는 선택지(options)가 없다")
        oids = [o.get("id") for o in opts]
        if len(set(oids)) != len(oids):
            problems.append(f"taxonomy/category[{c['id']}]: 선택지 id 가 겹친다")
        for o in opts:
            if o.get("group") not in ("spectrum", "rule") or not (o.get("text") or "").strip():
                problems.append(f"taxonomy/category[{c['id']}].options[{o.get('id')}]: "
                                f"group 은 spectrum·rule 중 하나이고 text 가 있어야 한다")
    return problems


def validate_all_for(voice_id: str | None) -> list[str]:
    """해석에 쓰일 층만 — 카탈로그 · 전역 · 그 voice."""
    problems = validate_catalog()
    if problems:
        return problems
    g = load_layer("global")
    problems += validate_layer("global", g)
    if voice_id and voice_path(voice_id).exists():
        problems += validate_layer(f"voice:{voice_id}", load_layer(f"voice:{voice_id}"),
                                   base_layers={"global": g})
    return problems


def layer_hashes() -> dict[str, str]:
    """lock 이 고정할 문체 설정 파일들. 기본 카탈로그도 규칙이다 — 플러그인이 바뀌면 lock 이 알아야 한다."""
    import hashlib

    def h(p: Path) -> str:
        return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()[:16]

    out = {"catalog/lexicon.json": h(LEXICON_CATALOG), "catalog/qualitative.json": h(QUALITATIVE_TAXONOMY)}
    if global_path().exists():
        out["global/style.json"] = h(global_path())
    return out


def validate_all() -> list[str]:
    """레지스트리 전체 — 전역과 모든 voice 의 문체 설정."""
    problems = validate_catalog()
    if problems:
        return problems
    g = load_layer("global")
    problems += validate_layer("global", g)
    for v in list_voices():
        if v["has_style"]:
            problems += validate_layer(f"voice:{v['id']}", load_layer(f"voice:{v['id']}"),
                                       base_layers={"global": g})
    return problems


# ── 렌더 — 모델이 읽는 지시문 ──────────────────────────────────────────────
def _forms_label(x: dict) -> str:
    if x.get("forms"):
        return "·".join(x["forms"][:4]) + ("…" if len(x["forms"]) > 4 else "")
    return x.get("label") or x["id"]


def _cat_path(cid: str, cats: dict[str, dict]) -> str:
    return " > ".join(c["label"] for c in _category_chain(cid, cats))


def render(eff: dict, *, profile: str = "worker", usage: str = "generate") -> str:
    """유효 문체 설정을 집필·채점 컨텍스트에 싣는 마크다운으로 편다.

    worker 는 목록 전부, main 은 개수와 게이트 항목 코드만. 가중치 0(보통) 항목은 싣지 않는다 —
    지시가 없는 항목까지 실으면 수백 줄이 컨텍스트를 먹는데 모델이 할 일은 없다.
    L0 에서 온 항목은 L0 문서가 이미 설명하므로 **바뀐 것만** 싣는다.
    """
    catalog = load_catalog()
    cats = _category_index(catalog)
    items = [x for x in eff["items"] if x["active"]]
    # L0 스캐너가 세는 항목(W·H·D 코드)은 L0 문서가 이미 표로 싣는다 — 바뀐 것만 다시 싣는다.
    shown = [x for x in items
             if x["weight"] != 0 and (not (x.get("l0") or {}).get("scanner") or x["weight_from"] != "default")]
    protected_l0 = [x for x in eff["items"]
                    if x.get("l0") and x.get("l0", {}).get("axis") in WAIVABLE
                    and (not x["active"] or x["weight"] > 0)]
    dirs = [d for d in eff["directives"] if d.get("enabled")]
    gated = [d for d in dirs if d.get("gate", {}).get("enabled")]

    L: list[str] = []
    L.append("### 문체 설정 — 전역 설정을 계승한 유효값")
    L.append("")
    L.append("> 기본 카탈로그 → 전역 → voice 순으로 겹친 결과다. 편집은 `authoring-style` 편집기에서 한다.")
    L.append("")
    if profile == "main":
        by_band: dict[int, int] = {}
        for x in shown:
            by_band[x["weight"]] = by_band.get(x["weight"], 0) + 1
        bands = " · ".join(f"{WEIGHT_BANDS[w]['name']}({w:+d}) {n}" for w, n in sorted(by_band.items()))
        L.append(f"- **어휘 목록** — 지시가 걸린 항목 {len(shown)}개" + (f": {bands}" if bands else ""))
        if protected_l0:
            L.append(f"- **L0 어휘 보호(항목 면제)** — " + ", ".join(_forms_label(x) for x in protected_l0[:8]))
        L.append(f"- **정성 지시** — {len(dirs)}개 · 게이트 채점 {len(gated)}개"
                 + (": " + ", ".join(f"`Q:{d['id']}`({d['gate']['level']})" for d in gated[:10]) if gated else ""))
        L.append("")
        L.append("> 목록 전문은 워커가 `resolve --profile worker` 로 읽는다.")
        return "\n".join(L)

    L.append("#### 어휘 목록 — 채택 가중치")
    L.append("")
    L.append("0 이 보통이다. 양수는 보통보다 적극, 음수는 보통보다 소극적으로 쓴다. "
             "음수 항목은 `scan_lexicon.py` 가 허용량을 넘는지 센다.")
    L.append("")
    if not shown:
        L.append("_가중치가 걸린 어휘가 없다._")
        L.append("")
    for wt in sorted({x["weight"] for x in shown}):
        band = WEIGHT_BANDS[wt]
        L.append(f"**{band['name']} ({wt:+d})** — {band['directive']}")
        group: dict[str, list[dict]] = {}
        for x in shown:
            if x["weight"] == wt:
                group.setdefault(x.get("category", ""), []).append(x)
        for cid in sorted(group):
            # 대안이 같은 항목은 한데 묶는다 — 같은 화살표가 열 번 반복되면 읽는 쪽이 지친다.
            by_alt: dict[tuple, list[str]] = {}
            for x in group[cid]:
                by_alt.setdefault(tuple(x.get("alternatives", [])[:2]), []).append(_forms_label(x))
            parts = [" · ".join(forms) + (f" → {' / '.join(alt)}" if alt else "") for alt, forms in by_alt.items()]
            L.append(f"- {_cat_path(cid, cats)}: " + " ; ".join(parts))
        L.append("")
    if protected_l0:
        L.append("**L0 기계 리듬 탐지에서 보호하는 어휘(항목 면제)** — 이 voice 의 색이다. 고치려 들지 마라.")
        for x in protected_l0:
            L.append(f"- `{x['l0'].get('code')}` {_forms_label(x)} — {x.get('reason') or '(사유 없음)'}")
        L.append("")

    L.append("#### 정성 지시")
    L.append("")
    if usage == "preserve":
        L.append("> 이 voice 는 `preserve` 다. 아래는 새로 쓰는 지침이 아니라 **다듬을 때 지킬 색**이다.")
        L.append("")
    if not dirs:
        L.append("_등록된 정성 지시가 없다._")
        L.append("")
    tax = {c["id"]: c for c in load_taxonomy().get("categories", [])}

    def tpath(cid: str) -> str:
        c = tax.get(cid, {})
        parent = tax.get(c.get("parent") or "", {})
        return (parent.get("label", "") + " > " if parent else "") + c.get("label", cid)

    for d in dirs:
        gate = d.get("gate", {})
        mark = f" · 게이트 {gate['level']}" if gate.get("enabled") else ""
        mark += " · 고른 선택지" if d.get("choice") else ""
        L.append(f"- **`Q:{d['id']}`** [{tpath(d.get('category', ''))} · `{d.get('axis')}`{mark}] {d['text'].strip()}")
        ex = d.get("example") or {}
        if ex.get("good"):
            L.append(f"  - ✓ {ex['good']}")
        if ex.get("bad"):
            L.append(f"  - ✗ {ex['bad']}")
    L.append("")
    if gated:
        L.append("#### 게이트 채점 항목 — 정성 지시 (Q)")
        L.append("")
        # 판정 규칙은 분류 체계가 갖는다 — 게이트 스킬과 해석 결과가 같은 문장을 보게.
        for rule in load_taxonomy().get("judging", {}).get("rules", []):
            L.append(f"> {rule}")
        L.append("")
        for d in gated:
            c = tax.get(d.get("category", ""), {})
            L.append(f"- **[{d['gate']['level']}] Q:{d['id']}** ({c.get('label', d.get('category'))}) — {d['text'].strip()}")
            if c.get("questions"):
                L.append(f"  - 판정 질문: " + " / ".join(c["questions"]))
        L.append("")
    return "\n".join(L).rstrip()


# ── 가중치 어휘 스캔 ─────────────────────────────────────────────────────
KO = "가-힣"


def compile_item(x: dict) -> re.Pattern | None:
    """항목 하나를 정규식으로. boundary=word 면 어절 머리에서만 잡는다(한국어엔 \\b 가 없다)."""
    if x.get("regex"):
        body = x["regex"]
    elif x.get("forms"):
        body = "|".join(re.escape(f) for f in sorted(x["forms"], key=len, reverse=True))
    else:
        return None
    head = rf"(?<![{KO}A-Za-z0-9])" if x.get("boundary", "word") == "word" else ""
    return re.compile(f"{head}(?:{body})")


def _sentence_hits(rx: re.Pattern, sent: str, mode: str) -> int:
    s = sent.strip().lstrip("\"'“‘(「『*_ ")
    if mode in ("sentence-initial", "paragraph-initial"):
        m = rx.match(s)
        return 1 if m else 0
    if mode == "sentence-final":
        tail = re.sub(r"[\s.!?…\"'”’)」』*_]+$", "", s)
        # 문장 끝까지 이어지는 일치만 — `…합니다` 가 `…합니다만,` 에 걸리지 않게.
        return 1 if any(m.end() == len(tail) for m in rx.finditer(tail)) else 0
    return len(rx.findall(s))


def allowed(weight: int, prose_chars: int, budget: dict | None = None) -> int | None:
    band = {**WEIGHT_BANDS[weight], **(budget or {})}
    if band.get("per_1000") is None:
        return None
    return max(int(band.get("min") or 0), int(band["per_1000"] * prose_chars / 1000))


def scan_lexicon(paragraphs: list[str], sentences_by_para: list[list[str]], eff: dict,
                 *, include_l0_scanned: bool = False) -> dict:
    """유효 어휘 목록으로 본문을 잰다.

    L0 스캐너(`scan_ai_style.py`)가 이미 세는 항목(`l0.scanner`)은 기본적으로 뺀다 — 한 항목을
    두 갈래에서 중복 판정하지 않는다. 판정 결과는 셋이다:

      over     음수 가중치 항목이 허용량을 넘었다 (금지는 1회부터)
      unused   +2 이상인데 한 번도 안 썼다 (+3 은 경고, +2 는 알림)
      counted  나머지 — 사용 횟수만 보고
    """
    catalog = load_catalog()
    cats = _category_index(catalog)
    prose_chars = sum(len(p) for p in paragraphs)
    n_sent = sum(len(s) for s in sentences_by_para)
    rows = []
    stack_hits: dict[str, list[str]] = {}
    for x in eff["items"]:
        if not x["active"]:
            continue
        if x.get("l0", {}).get("scanner") and not include_l0_scanned:
            continue
        rx = compile_item(x)
        if rx is None:
            continue
        exc = re.compile(x["except"]) if x.get("except") else None
        mode = x.get("mode", "count")
        n, where = 0, []
        for pi, sents in enumerate(sentences_by_para):
            for si, s in enumerate(sents):
                if mode == "paragraph-initial" and si != 0:
                    continue
                if exc and exc.search(s):
                    continue
                k = _sentence_hits(rx, s, mode)
                if k:
                    n += k
                    if len(where) < 3:
                        where.append(s[:60] + ("…" if len(s) > 60 else ""))
        row = {"id": x["id"], "forms": _forms_label(x), "category": x.get("category"),
               "category_path": _cat_path(x.get("category", ""), cats),
               "weight": x["weight"], "count": n, "mode": mode, "where": where,
               "alternatives": x.get("alternatives", []), "l0": x.get("l0")}
        lim = allowed(x["weight"], prose_chars, x.get("budget")) if x["weight"] < 0 else None
        if lim is not None and n > lim:
            row["verdict"] = "over"
            row["allowed"] = lim
        elif x["weight"] >= 2 and n == 0 and prose_chars >= 800:
            row["verdict"] = "unused"
        else:
            row["verdict"] = "counted"
        if mode == "sentence-final" and n_sent:
            row["share"] = round(n / n_sent, 3)
        if n or x["weight"] != 0:
            rows.append(row)

    # 카테고리 단위 점검 — 분류가 선언한 것만. 한 문장 안에 같은 분류가 겹치는지(stack),
    # 분류 전체가 1,000자당 얼마나 나오는지(density).
    cat_findings = []
    for c in eff["categories"]:
        if not c.get("active", True):
            continue
        chk = c.get("check", {})
        # 양수 가중치 항목은 뺀다 — voice 가 즐겨 쓰겠다고 한 어휘를 밀도 초과로 세면 판정이 뒤집힌다.
        members = [x for x in eff["items"] if x["active"] and x["weight"] <= 0
                   and (x.get("category") == c["id"] or x.get("category", "").startswith(c["id"] + "."))]
        if not members:
            continue
        rxs = [(compile_item(x), re.compile(x["except"]) if x.get("except") else None) for x in members]
        rxs = [(r, e) for r, e in rxs if r is not None]
        if chk.get("stack"):
            bad = []
            for sents in sentences_by_para:
                for s in sents:
                    # 겹침은 **등장 횟수**로 센다 — 'A의 B의 C' 처럼 같은 항목이 반복돼도 겹침이다.
                    k = sum(len(r.findall(s)) for r, e in rxs if not (e and e.search(s)))
                    if k >= chk["stack"]:
                        bad.append(s[:60])
            if bad:
                cat_findings.append({"category": c["id"], "label": c["label"], "kind": "stack",
                                     "threshold": chk["stack"], "count": len(bad), "where": bad[:3]})
        if chk.get("density_per_1000") and prose_chars:
            total = sum(len(r.findall(s)) for r, e in rxs for sents in sentences_by_para for s in sents
                        if not (e and e.search(s)))
            dens = total * 1000 / prose_chars
            # 짧은 글에서는 두어 번만 나와도 밀도가 치솟는다 — 3회 미만은 밀도로 판정하지 않는다.
            if total >= 3 and dens > chk["density_per_1000"]:
                cat_findings.append({"category": c["id"], "label": c["label"], "kind": "density",
                                     "threshold": chk["density_per_1000"], "count": total,
                                     "density": round(dens, 2)})
    over = [r for r in rows if r["verdict"] == "over"]
    unused = [r for r in rows if r["verdict"] == "unused"]
    return {
        "prose_chars": prose_chars,
        "sentences": n_sent,
        "over": over,
        "unused": unused,
        "category": cat_findings,
        "rows": rows,
        "forbidden_hits": sum(r["count"] for r in over if r["weight"] == -3),
        "pass": not over and not any(u["weight"] >= 3 for u in unused) and not cat_findings,
    }


def l0_lists(eff: dict | None = None) -> dict[str, list[dict]]:
    """L0 스캐너가 쓸 어휘 목록 — 코드별로, 켜져 있고 가중치가 0 이하인 항목만.

    voice 가 L0 항목을 끄거나 양수로 올렸다면 그 항목은 **항목 단위로 면제**된 것이라 빠진다
    (reason 은 validate 가 강제한다). eff 가 없으면 플러그인 기본값만 쓴다 —
    레지스트리 없이 단독으로 도는 스캐너의 판정이 사용자 설정에 흔들리지 않게.
    """
    if eff is None:
        cats = _category_index(load_catalog())
        items = [_norm_item(it, "default", cats) for it in load_catalog().get("items", [])]
        for x in items:
            x["active"] = x["enabled"]
    else:
        items = eff["items"]
    out: dict[str, list[dict]] = {}
    for x in items:
        codes = (x.get("l0") or {}).get("scanner")
        if not codes:
            continue
        if not x["active"] or x["weight"] > 0:
            continue
        for code in ([codes] if isinstance(codes, str) else codes):
            out.setdefault(code, []).append(x)
    return out
