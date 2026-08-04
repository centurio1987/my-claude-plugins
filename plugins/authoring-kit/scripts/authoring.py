#!/usr/bin/env python3
"""authoring-kit 레지스트리 해석기.

집필 규칙은 세 층에 나뉘어 산다.

    L0  공통 원칙   ~/.claude/authoring/principles/     모든 voice에 적용
    L1  퍼소나 voice ~/.claude/authoring/voices/<id>/    그 퍼소나에만 적용
    L2  글 명세      <project>/.claude/authoring/specs/  그 글 종류에만 적용

층에 전역 서열을 매기지 않는다. 대신 **갈래(axis)마다 소유 층을 하나로 못박고, 소유자만 그 갈래의
규칙을 쓴다.** 서열을 매기면 "누가 이기냐"가 층 단위로 전파되어, 한 사람의 문체가 전역 규칙으로
승격되는 사고가 재발한다 — 이 도구는 그 사고를 막으려고 존재한다.

    evidence · grammar · comprehension   L0 단독 (불가침, waiver 불가)
    machine-rhythm                       L0 탐지 + L1 면제
    register/rhythm/device/lexicon       L1 단독
    structure/scope-principle            L2 단독

핵심 커맨드는 `resolve` 다. 집필 에이전트는 L0/L1/L2 문서를 각자 읽지 않고 **병합 결과 한 벌만**
읽는다. 지금까지는 스킬마다 서너 개 문서를 각자 읽어 순서·조합이 매번 흔들렸는데, 그걸 고정하는
것이 재현성의 기계적 토대다.

사용법:
    authoring.py status  [project_dir]
    authoring.py list    voices | specs [project_dir]
    authoring.py show    voice <id> | spec <id>
    authoring.py resolve --voice <id> [--spec <id>] [--project <dir>] [--out <file>]
    authoring.py validate --voice <id> | --spec <id> | --all
    authoring.py path    [--scope voices|specs|principles]

상태 위치 해석(첫 번째로 쓸 수 있는 것):
    1. $AUTHORING_KIT_HOME              명시 오버라이드 (스크래치 검증에 쓴다)
    2. ~/.claude/authoring/             기본 — PRIVATE 백업 레포로 버전관리된다
    3. <plugin>/assets 의 upstream 기본값 (읽기 전용 폴백)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))
UPSTREAM_ASSETS = PLUGIN_ROOT / "skills" / "authoring-method" / "assets"

# ── 갈래 소유권 ────────────────────────────────────────────────────────────
AXIS_OWNER = {
    "evidence": "L0",
    "grammar": "L0",
    "comprehension": "L0",
    "machine-rhythm": "L0",
    "register": "L1",
    "rhythm": "L1",
    "device": "L1",
    "lexicon": "L1",
    "structure": "L2",
    "scope-principle": "L2",
}
# `comprehension` 이 따로 있는 이유: "점진적 공개 · 약어 첫 등장 풀어쓰기 · 미정의 용어 없음"
# 같은 항목은 글 종류를 가리지 않는 공통 원칙인데, 담을 축이 없었다.
#   structure 는 L2 단독이라 L0 문서가 쓰면 갈래 위반이고,
#   grammar(문장이 한국어다운가)도 evidence(사실이 맞는가)도 아니다.
# 억지로 기존 축에 밀어 넣으면 라벨이 거짓이 되므로 축을 하나 늘렸다.
HARD_FLOOR = {"evidence", "grammar", "comprehension"}   # 어떤 voice도 무력화할 수 없다
WAIVABLE = {"machine-rhythm"}                            # 유일한 협상 대상

AXIS_TAG = re.compile(r"<!--\s*axis:\s*([a-z-]+)\s*-->")

# 순서가 곧 집필 컨텍스트에 실리는 순서다. 원칙 → 문장 → 박자 → 채점 순으로,
# "무엇을 지켜야 하는가"에서 "무엇으로 판정받는가"로 좁혀 간다.
L0_FILES = [
    "L0_PRINCIPLES.md",
    "L0_NATURAL_KOREAN.md",
    "L0_MACHINE_RHYTHM.md",
    "QUALITY_RUBRIC.md",
]


# ── 위치 해석 ────────────────────────────────────────────────────────────
def registry_home() -> Path:
    override = os.environ.get("AUTHORING_KIT_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".claude" / "authoring"


def principles_dir() -> Path:
    """user override 가 있으면 그것, 없으면 플러그인 동봉 upstream."""
    p = registry_home() / "principles"
    if p.is_dir() and any(p.glob("L0_*.md")):
        return p
    return UPSTREAM_ASSETS


def voices_dir() -> Path:
    return registry_home() / "voices"


def _git(project_dir: Path, *args: str) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(project_dir), *args],
                           capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return None


def project_identity(project_dir: Path) -> tuple[str, str]:
    """(사람이 읽는 라벨, 안정 키). git remote > toplevel > 절대경로 순으로 잡는다.

    remote 를 우선하는 이유는 워크트리·클론이 달라도 같은 프로젝트로 묶이기 때문이다.
    스크래치 워크트리와 원본이 같은 spec 을 보게 하려면 이 성질이 필요하다.
    """
    remote = _git(project_dir, "config", "--get", "remote.origin.url")
    top = _git(project_dir, "rev-parse", "--show-toplevel")
    if remote:
        basis, label = remote, remote.rsplit("/", 1)[-1].removesuffix(".git")
    elif top:
        basis, label = top, Path(top).name
    else:
        basis = str(project_dir.resolve())
        label = project_dir.resolve().name
    return label, hashlib.sha1(basis.encode("utf-8")).hexdigest()[:12]


def specs_dir(project_dir: Path) -> Path:
    top = _git(project_dir, "rev-parse", "--show-toplevel")
    root = Path(top) if top else project_dir.resolve()
    return root / ".claude" / "authoring" / "specs"


def sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ── 로드 ─────────────────────────────────────────────────────────────────
def load_voice(vid: str) -> tuple[dict, str]:
    d = voices_dir() / vid
    j, m = d / "voice.json", d / "voice.md"
    if not j.exists():
        raise FileNotFoundError(f"voice 를 찾을 수 없다: {vid}  ({j})")
    return json.loads(j.read_text(encoding="utf-8")), (m.read_text(encoding="utf-8") if m.exists() else "")


def load_spec(sid: str, project_dir: Path) -> tuple[dict, str]:
    d = specs_dir(project_dir) / sid
    j, m = d / "spec.json", d / "spec.md"
    if not j.exists():
        raise FileNotFoundError(f"spec 을 찾을 수 없다: {sid}  ({j})")
    return json.loads(j.read_text(encoding="utf-8")), (m.read_text(encoding="utf-8") if m.exists() else "")


def load_l0() -> list[tuple[str, str]]:
    base = principles_dir()
    out = []
    for name in L0_FILES:
        p = base / name
        if p.exists():
            out.append((name, p.read_text(encoding="utf-8")))
    return out


def l0_index() -> list[str]:
    """L0 전문 대신 **코드 목록만** 뽑는다.

    왜 필요한가: L0 네 문서를 통째로 실으면 해석 결과가 1000줄을 넘는다. 메인 스레드가
    그걸 다 안고 가면 정작 글을 쓸 예산이 남지 않는다. 메인은 "어떤 규칙이 걸려 있는지"만
    알면 되고, 조항 전문은 실제로 문장을 다듬는 워커(`authoring-method`)가 읽으면 된다.
    web-research 플러그인에서 검증된 분리다.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import trace_rules as tr  # type: ignore
    except Exception:
        return ["(코드 목록을 만들 수 없다 — trace_rules.py 를 찾지 못했다)"]

    lines: list[str] = []
    base = principles_dir()
    for name in L0_FILES:
        p = base / name
        if not p.exists():
            continue
        rules = [r for r in tr.extract(p) if r["_ruleish"]]
        if not rules:
            continue
        axes = sorted({r["axis"] for r in rules if r["axis"]})
        lines.append(f"\n**{name}** — 축 `{'` · `'.join(axes)}` · {len(rules)}개 조항")
        # 코드와 한 줄 제목만. 판정선·예시·대안은 워커가 전문에서 읽는다.
        buf = [f"`{r['rule_id']}` {r['title'][:34]}" for r in rules]
        for i in range(0, len(buf), 3):
            lines.append("  " + " · ".join(buf[i:i + 3]))
    return lines


# ── validate ─────────────────────────────────────────────────────────────
def check_l0_axes(problems: list[str]) -> None:
    """L0 문서에 L1/L2 소유 축이 선언돼 있으면 갈래 위반이다."""
    for name, text in load_l0():
        for m in AXIS_TAG.finditer(text):
            axis = m.group(1)
            if axis not in AXIS_OWNER:
                problems.append(f"L0/{name}: 알 수 없는 축 '{axis}'")
            elif AXIS_OWNER[axis] != "L0":
                problems.append(
                    f"L0/{name}: 갈래 위반 — '{axis}' 는 {AXIS_OWNER[axis]} 단독 소유인데 L0 문서가 선언했다")


def validate_voice(v: dict, problems: list[str]) -> None:
    vid = v.get("id", "(id 없음)")
    for axis in v.get("axes", {}):
        if axis not in AXIS_OWNER:
            problems.append(f"voice/{vid}: 알 수 없는 축 '{axis}'")
        elif AXIS_OWNER[axis] != "L1":
            problems.append(
                f"voice/{vid}: 갈래 위반 — '{axis}' 는 {AXIS_OWNER[axis]} 소유다. voice 가 선언할 수 없다")
    for w in v.get("waivers", []):
        target = w.get("target", "")
        axis = target.split(":", 1)[1] if ":" in target else target
        if axis in HARD_FLOOR:
            problems.append(
                f"voice/{vid}: waiver 거부 — '{axis}' 는 hard floor 다. "
                f"어떤 voice도 무력화할 수 없다 (code={w.get('code')})")
        elif axis not in WAIVABLE:
            problems.append(
                f"voice/{vid}: waiver 대상이 아닌 축 '{axis}' (code={w.get('code')}). "
                f"면제 가능한 갈래은 {sorted(WAIVABLE)} 뿐이다")
        if not w.get("reason"):
            problems.append(f"voice/{vid}: waiver({w.get('code')}) 에 reason 이 없다 — 조용한 면제는 금지")
    if v.get("status") not in {"defined", "draft", "undefined"}:
        problems.append(f"voice/{vid}: status 가 defined|draft|undefined 중 하나여야 한다")
    # `usage` 는 **이 목소리로 쓰는가, 이 목소리를 지키는가**를 가른다.
    # `kind`(human|ai-persona)로는 못 가른다 — `yundeok` 은 사람이지만 AI 가 그 목소리로 이력서를 쓴다.
    # 이 구분이 없으면 "사용자가 직접 쓰는 저자"의 문체를 생성 지침으로 오해한다(실제로 그랬다).
    # `defined` 는 "집필에 바로 쓸 수 있다"는 선언이다. 사람이 읽는 확장판이 없으면
    # 그 선언이 거짓이다 — 실제로 확장판 없이 `defined` 인 voice 로 글이 한 편 나갔다.
    if v.get("status") == "defined" and not (voices_dir() / vid / "voice.md").exists():
        problems.append(
            f"voice/{vid}: status 가 defined 인데 voice.md 가 없다. "
            f"확장판 없이 defined 로 두면 집필 에이전트가 축 선언만 보고 쓰게 된다 — "
            f"voice.md 를 쓰거나 status 를 draft 로 내려라")
    if v.get("usage") not in {"generate", "preserve"}:
        problems.append(
            f"voice/{vid}: usage 가 generate|preserve 중 하나여야 한다. "
            f"generate=AI 가 이 목소리로 집필한다 · preserve=사람이 쓴 글을 손볼 때 지킬 색이다")


def validate_spec(s: dict, problems: list[str]) -> None:
    sid = s.get("id", "(id 없음)")
    for pr in s.get("principles", []):
        axis = pr.get("axis")
        if axis not in AXIS_OWNER:
            problems.append(f"spec/{sid}: 알 수 없는 축 '{axis}' (code={pr.get('code')})")
        elif AXIS_OWNER[axis] not in {"L2", "L0"}:
            problems.append(
                f"spec/{sid}: 갈래 위반 — principles 의 '{axis}' 는 {AXIS_OWNER[axis]} 소유다 "
                f"(code={pr.get('code')}). spec 은 structure·scope-principle·evidence 만 쓴다")
        if pr.get("level") not in {"MUST", "SHOULD", "IF-APPLICABLE"}:
            problems.append(f"spec/{sid}: level 이 MUST|SHOULD|IF-APPLICABLE 이 아니다 (code={pr.get('code')})")
    if "voice" in s:
        default = s["voice"].get("default")
        if default:
            try:
                load_voice(default)
            except FileNotFoundError:
                problems.append(f"spec/{sid}: voice.default '{default}' 가 레지스트리에 없다")


# ── resolve ──────────────────────────────────────────────────────────────
def render_voice_json(v: dict) -> str:
    """voice.md 가 없을 때 voice.json 으로 L1 을 채운다.

    `voice.md` 는 사람이 읽는 확장판이고 `voice.json` 은 기계가 읽는 축 선언이다.
    확장판이 아직 없다고 **축 선언까지 버리면 목소리가 통째로 사라진다.** 덜 풍부할 뿐
    같은 규칙이므로, 없으면 이쪽을 편다. 그리고 **없다는 사실을 함께 적는다** —
    조용히 메우면 확장판이 영영 안 써진다.
    """
    L = [f"> **`voice.md` 가 아직 없어 `voice.json` 의 축 선언으로 대신한다.**",
         f"> 사람이 읽는 확장판을 쓰면 이 자리가 그것으로 바뀐다.", "",
         f"# {v.get('label', v.get('id'))} — 문체 선언", ""]
    for axis in ("register", "rhythm", "device", "lexicon"):
        val = v.get("axes", {}).get(axis)
        if not val:
            continue
        L.append(f"## {axis}")
        L.append("")
        L.extend([f"- {x}" for x in val] if isinstance(val, list) else [val])
        L.append("")
    if v.get("forbid"):
        L += ["## 금지", ""] + [f"- {x}" for x in v["forbid"]] + [""]
    if v.get("params"):
        L += ["## 파라미터", ""] + [f"- `{k}`: {x}" for k, x in v["params"].items()] + [""]
    if v.get("waivers"):
        L += ["## 이 voice 가 L0 에 대해 선언한 면제", ""]
        L += [f"- `{w.get('code')}` ({w.get('target')}) — {w.get('reason')}"
              f"{' / 해제 조건: ' + w['limit'] if w.get('limit') else ''}" for w in v["waivers"]]
        L.append("")
    return "\n".join(L).strip()


class VoiceEmpty(Exception):
    """L1 에 실을 것이 없을 때. **조용히 빈 문서를 내주지 않기 위한 예외.**"""


def _has_voice_substance(rendered: str, v: dict) -> bool:
    """이 voice 가 집필 지침으로 쓸 만한 내용을 실제로 갖고 있는가.

    네 항목(register·rhythm·device·lexicon) 중 **최소 둘**은 채워져 있어야 한다.
    하나만 있으면 그건 목소리가 아니라 메모다.
    """
    axes = v.get("axes", {})
    filled = [k for k in ("register", "rhythm", "device", "lexicon") if axes.get(k)]
    return len(filled) >= 2 and len(rendered.strip()) >= 200


def resolve(voice_id: str, spec_id: str | None, project_dir: Path,
            profile: str = "worker") -> tuple[str, dict]:
    """L0+L1+L2 를 한 벌로 병합한다.

    profile:
      worker  전문 전부. 실제로 문장을 쓰고 채점하는 서브에이전트가 읽는다.
      main    L0 는 **코드 목록만**. 메인 스레드가 오케스트레이션에 필요한 만큼만 읽는다.

    두 프로파일의 해시는 다르다 — 서로 다른 문서이기 때문이다. 산출물 보고에는
    worker 해시를 기록한다(그 규칙으로 글이 쓰였으므로).
    """
    problems: list[str] = []
    v, v_md = load_voice(voice_id)
    validate_voice(v, problems)
    check_l0_axes(problems)

    s = s_md = None
    if spec_id:
        s, s_md = load_spec(spec_id, project_dir)
        validate_spec(s, problems)
        allowed = s.get("voice", {}).get("allowed")
        if allowed and voice_id not in allowed:
            problems.append(
                f"CONFLICT: spec '{spec_id}' 는 voice {allowed} 만 허용하는데 '{voice_id}' 로 해석하려 한다")

    waived = {w["code"] for w in v.get("waivers", [])}
    parts: list[str] = []
    parts.append(f"# 해석된 집필 규칙 — voice `{voice_id}`" + (f" · spec `{spec_id}`" if spec_id else ""))
    parts.append("")
    parts.append("> 이 문서는 `authoring.py resolve` 가 L0+L1+L2 를 병합해 만든 **파생물**이다.")
    parts.append("> 직접 고치지 마라 — 원본을 고치고 다시 해석한다.")
    parts.append("")

    parts.append("## 적용 요약")
    parts.append("")
    parts.append(f"- **voice**: `{voice_id}` ({v.get('label','')}) · status `{v.get('status')}` · kind `{v.get('kind')}`")
    if v.get("status") == "undefined":
        parts.append("  - ⚠ 이 퍼소나는 아직 voice 가 정의되지 않았다. 집필 전에 정의하거나 다른 voice 를 고른다.")
    elif v.get("status") == "draft":
        parts.append("  - ⚠ 초안 상태다. 사람 승인 전까지 이 voice 로 발행하지 않는다.")
    parts.append(f"- **면제된 machine-rhythm 코드**: {sorted(waived) if waived else '없음'}")
    parts.append(f"- **hard floor**: {sorted(HARD_FLOOR)} — 면제 불가")
    if spec_id:
        parts.append(f"- **spec**: `{spec_id}` ({s.get('label','')}) · 섹션 {len(s.get('sections', []))}개")
    parts.append("")

    parts.append("## L1 — 이 글의 목소리 (register · rhythm · device · lexicon)")
    parts.append("")
    if profile == "main":
        for axis in ("register", "rhythm", "lexicon"):
            val = v.get("axes", {}).get(axis)
            if val:
                parts.append(f"- **{axis}** — {val}")
        dev = v.get("axes", {}).get("device")
        if dev:
            parts.append(f"- **device** — {', '.join(dev) if isinstance(dev, list) else dev}")
        if v.get("forbid"):
            parts.append(f"- **금지** — {' · '.join(v['forbid'])}")
        parts.append("")
        parts.append("> 예문과 근거를 포함한 전문은 집필 단계에서 `authoring-method` 가 로드한다.")
    else:
        # voice.md 가 없다고 **L1 을 비워 보내지 않는다.** 그러면 집필 에이전트가
        # 퍼소나 규칙을 하나도 못 본 채 쓰게 되고, 아무도 그 사실을 모른다 —
        # 실제로 그렇게 한 편이 쓰였다. 같은 정보가 voice.json 에 있으므로 거기서 편다.
        # **L1 이 비면 해석 자체를 거부한다.**
        # 예전에는 `_voice.md 없음_` 한 줄을 싣고 넘어갔고, 그 결과 집필 에이전트가
        # 퍼소나 규칙을 하나도 못 본 채 글을 한 편 썼다. 아무도 몰랐고 워커가 우연히
        # 짚어 줘서 발견했다. **퍼소나를 분리해 관리하는 구조를 만들어 놓고 퍼소나 없이
        # 글이 나가면 그 구조가 무의미하다.** 대체 렌더는 정보 손실을 줄일 뿐 이 사고를
        # 막지 못한다 — 막는 것은 여기서 죽는 것이다.
        l1 = v_md.strip() or render_voice_json(v)
        if not _has_voice_substance(l1, v):
            raise VoiceEmpty(
                f"voice '{voice_id}' 에 실을 문체 규칙이 없다.\n"
                f"  voice.md 도 없고 voice.json 의 axes 도 비어 있다.\n"
                f"  이 상태로는 집필 에이전트가 퍼소나 규칙을 못 본 채 쓰게 되므로 해석을 중단한다.\n"
                f"  `authoring-voice` 로 등록을 마치거나 status 를 draft 로 내려라.")
        parts.append(l1)
    parts.append("")

    if s:
        parts.append("## L2 — 이 글 종류의 명세 (structure · scope-principle)")
        parts.append("")
        if profile == "main":
            parts.append("### 항목 골격")
            parts.append("")
            parts.append("| 순서 | id | 항목 | 필수 | 헤딩 고정 |")
            parts.append("| --- | --- | --- | --- | --- |")
            for x in sorted(s.get("sections", []), key=lambda z: z.get("order", 0)):
                req = "필수" if x.get("required") else ("조건부" if x.get("condition") else "선택")
                fixed = "고정" if x.get("heading_fixed") else ""
                parts.append(f"| {x.get('order','')} | `{x['id']}` | {x['label']} | {req} | {fixed} |")
            parts.append("")
            if s.get("conditional_rule"):
                parts.append(f"> {s['conditional_rule']}")
                parts.append("")
            parts.append("> 항목별 작성 방법(`spec.md`)은 집필 단계에서 로드한다.")
            parts.append("")
        elif s_md:
            parts.append(s_md.strip())
            parts.append("")

    if s and s.get("principles"):
        parts.append("### 이 글 범위의 원칙")
        parts.append("")
        for pr in s["principles"]:
            parts.append(f"- **{pr['code']}** ({pr['level']} · {pr['axis']}) — {pr['text']}")
        parts.append("")

    if profile == "main":
        parts.append("## L0 — 걸려 있는 공통 원칙 (코드 목록)")
        parts.append("")
        parts.append("> 조항 전문은 여기 싣지 않는다. 문장을 실제로 쓰고 채점하는 단계에서")
        parts.append("> `authoring-method` 스킬이 전문을 로드한다 — 메인 스레드의 예산을 지키기 위한 분리다.")
        parts.append("> 전문이 필요하면 `authoring.py resolve … --profile worker`.")
        parts.extend(l0_index())
        parts.append("")
        if waived:
            parts.append("**이 voice 에서 면제된 코드**: "
                         + ", ".join(f"`{c}`" for c in sorted(waived))
                         + " — 적발하지 않는다.")
            parts.append("")
    else:
        parts.append("## L0 — 모든 voice에 적용되는 공통 원칙")
        parts.append("")
        for name, text in load_l0():
            body = text
            if waived:
                body += ("\n\n> **이 voice 에서 면제된 코드**: "
                         + ", ".join(f"`{c}`" for c in sorted(waived))
                         + " — 위 표에서 해당 코드는 적발하지 않는다. 사유는 L1 의 면제 표에 있다.\n")
            parts.append(f"<!-- from: {name} -->")
            parts.append(body.strip())
            parts.append("")

    doc = "\n".join(parts).rstrip() + "\n"
    meta = {
        "voice": voice_id,
        "spec": spec_id,
        "profile": profile,
        "waived": sorted(waived),
        "conflicts": problems,
        "hash": sha256(doc),
    }
    return doc, meta


# ── 커맨드 ───────────────────────────────────────────────────────────────
def cmd_status(args) -> int:
    pd = Path(args.project_dir or ".").expanduser()
    label, key = project_identity(pd)
    vd, sd = voices_dir(), specs_dir(pd)
    voices = sorted(p.name for p in vd.glob("*/")) if vd.is_dir() else []
    specs = sorted(p.name for p in sd.glob("*/")) if sd.is_dir() else []
    print(json.dumps({
        "project": label,
        "key": key,
        "registry_home": str(registry_home()),
        "principles_dir": str(principles_dir()),
        "principles_source": "user-override" if principles_dir() != UPSTREAM_ASSETS else "plugin-upstream",
        "voices": voices,
        "specs_dir": str(sd),
        "specs": specs,
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_list(args) -> int:
    if args.what == "voices":
        d = voices_dir()
        if not d.is_dir():
            print("(등록된 voice 없음)"); return 0
        for p in sorted(d.glob("*/voice.json")):
            v = json.loads(p.read_text(encoding="utf-8"))
            mark = {"defined": " ", "draft": "~", "undefined": "!"}.get(v.get("status"), "?")
            print(f" {mark} {v['id']:18s} {v.get('label',''):12s} {v.get('kind',''):10s} "
                  f"waivers={len(v.get('waivers', []))}")
    else:
        d = specs_dir(Path(args.project_dir or ".").expanduser())
        if not d.is_dir():
            print("(등록된 spec 없음)"); return 0
        for p in sorted(d.glob("*/spec.json")):
            s = json.loads(p.read_text(encoding="utf-8"))
            print(f"   {s['id']:18s} {s.get('label',''):12s} "
                  f"voice={s.get('voice',{}).get('default','-')} 섹션={len(s.get('sections',[]))}")
    return 0


def cmd_show(args) -> int:
    if args.kind == "voice":
        v, md = load_voice(args.id)
        print(json.dumps(v, ensure_ascii=False, indent=2)); print(); print(md)
    else:
        s, md = load_spec(args.id, Path(args.project_dir or ".").expanduser())
        print(json.dumps(s, ensure_ascii=False, indent=2)); print(); print(md)
    return 0


def cmd_resolve(args) -> int:
    pd = Path(args.project or ".").expanduser()
    try:
        return _cmd_resolve(args, pd)
    except VoiceEmpty as e:
        print(f"해석 중단 — {e}", file=sys.stderr)
        return 1


def _cmd_resolve(args, pd: Path) -> int:
    # 재현성의 마지막 고리 — 전역 저장이라 프로젝트 checkout 만으로는 규칙 조합이 확정되지 않는다.
    # lock 이 그걸 메우는데, **어긋난 채로 조용히 집필하면 lock 이 있으나 마나다.**
    if getattr(args, "frozen", False):
        drift = lock_drift(pd)
        if drift:
            print("lock 과 어긋난 상태로는 집필하지 않는다 (--frozen):", file=sys.stderr)
            for d in drift:
                print(f"  {d}", file=sys.stderr)
            print("\n`authoring.py lock --update` 로 갱신하고 왜 바뀌었는지 커밋에 남긴다.",
                  file=sys.stderr)
            return 1
    doc, meta = resolve(args.voice, args.spec, pd, profile=args.profile)
    if meta["conflicts"]:
        for c in meta["conflicts"]:
            print(f"CONFLICT: {c}", file=sys.stderr)
        print("\n미해결 충돌이 있어 해석을 중단한다. 조용히 한쪽을 이기게 하지 않는다.", file=sys.stderr)
        return 1
    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(doc, encoding="utf-8")
        print(f"{out}  ({meta['hash']})")
    else:
        sys.stdout.write(doc)
    return 0


def cmd_validate(args) -> int:
    problems: list[str] = []
    check_l0_axes(problems)
    if args.voice or args.all:
        ids = [args.voice] if args.voice else [p.name for p in sorted(voices_dir().glob("*/"))]
        for vid in ids:
            try:
                v, _ = load_voice(vid)
                validate_voice(v, problems)
            except Exception as e:
                problems.append(str(e))
    if args.spec or args.all:
        pd = Path(args.project or ".").expanduser()
        sd = specs_dir(pd)
        ids = [args.spec] if args.spec else ([p.name for p in sorted(sd.glob("*/"))] if sd.is_dir() else [])
        for sid in ids:
            try:
                s, _ = load_spec(sid, pd)
                validate_spec(s, problems)
            except Exception as e:
                problems.append(str(e))
    if problems:
        for p in problems:
            print(f"  {p}")
        print(f"\n{len(problems)}건 실패")
        return 1
    print("통과 — 갈래 위반 0 · waiver 타깃 정상 · 참조 해소 정상")
    return 0


def lock_path(project_dir: Path) -> Path:
    top = _git(project_dir, "rev-parse", "--show-toplevel")
    root = Path(top) if top else project_dir.resolve()
    return root / ".claude" / "authoring.lock.json"


def build_lock(project_dir: Path) -> dict:
    """이 프로젝트가 지금 어떤 규칙 조합 위에 서 있는지 고정한다.

    voice 와 공통 원칙은 전역(`~/.claude/authoring/`)에 살기 때문에, 프로젝트를 checkout
    하는 것만으로는 규칙이 확정되지 않는다. 같은 커밋을 다른 머신에서 열면 다른 문체 규칙으로
    글이 나갈 수 있다. lock 이 그 구멍을 메운다 — **프로젝트 git 이 갖는 유일한 규칙 스냅샷**이다.
    """
    home = registry_home()
    pdir = principles_dir()
    principles = {p.name: sha256(p.read_text(encoding="utf-8"))
                  for p in sorted(pdir.glob("*.md"))}
    voices = {}
    if voices_dir().is_dir():
        for d in sorted(voices_dir().glob("*/")):
            blob = ""
            for f in ("voice.json", "voice.md"):
                fp = d / f
                if fp.exists():
                    blob += fp.read_text(encoding="utf-8")
            if blob:
                voices[d.name] = sha256(blob)
    sd = specs_dir(project_dir)
    specs = {}
    if sd.is_dir():
        for d in sorted(sd.glob("*/")):
            blob = ""
            for f in ("spec.json", "spec.md", "template.slots.json"):
                fp = d / f
                if fp.exists():
                    blob += fp.read_text(encoding="utf-8")
            if blob:
                specs[d.name] = sha256(blob)

    manifest = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
    ver = json.loads(manifest.read_text(encoding="utf-8"))["version"] if manifest.exists() else "?"
    label, key = project_identity(project_dir)
    return {
        "$schema": "authoring-kit/lock@1",
        "schema_version": 1,
        "project": {"label": label, "key": key},
        "plugin": {"name": "authoring-kit", "version": ver},
        "principles": {
            "source": str(pdir),
            "remote": _git(home, "config", "--get", "remote.origin.url"),
            "revision": _git(home, "rev-parse", "HEAD"),
            "files": principles,
        },
        "voices": voices,
        "specs": specs,
    }


def lock_drift(project_dir: Path) -> list[str]:
    """lock 이 기록한 규칙 조합과 지금 디스크의 상태가 어긋난 지점.

    `lock` 과 `resolve --frozen` 이 **같은 잣대**를 써야 한다 — 둘이 따로 세면
    "lock 은 통과인데 resolve 는 실패" 같은 답이 나오고, 그러면 어느 쪽도 못 믿는다.
    """
    lp = lock_path(project_dir)
    if not lp.exists():
        return ["lockfile 이 없다"]
    old = json.loads(lp.read_text(encoding="utf-8"))
    fresh = build_lock(project_dir)
    drift = []
    # 저장 위치가 바뀌면 해시가 같아도 재현 경로가 달라진다 — 스크래치에서 승격할 때 실제로 그랬다.
    a_src = old.get("principles", {}).get("source")
    b_src = fresh.get("principles", {}).get("source")
    if a_src != b_src:
        drift.append(f"principles.source: {a_src} → {b_src}")
    for group in ("principles", "voices", "specs"):
        a = old.get(group, {}).get("files", old.get(group, {}))
        b = fresh.get(group, {}).get("files", fresh.get(group, {}))
        if not isinstance(a, dict) or not isinstance(b, dict):
            continue
        for k in sorted(set(a) | set(b)):
            if a.get(k) != b.get(k):
                drift.append(f"{group}/{k}: "
                             f"{'추가됨' if k not in a else '없어짐' if k not in b else '내용 변경'}")
    return drift


def cmd_lock(args) -> int:
    pd = Path(args.project or ".").expanduser()
    lp = lock_path(pd)
    fresh = build_lock(pd)
    if args.update or not lp.exists():
        lp.parent.mkdir(parents=True, exist_ok=True)
        lp.write_text(json.dumps(fresh, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{lp}")
        print(f"  원칙 {len(fresh['principles']['files'])}개 · voice {len(fresh['voices'])}개 · spec {len(fresh['specs'])}개")
        return 0

    stale = lock_drift(pd)
    if stale:
        print("lock 이 현재 상태와 어긋난다 (stale):")
        for s in stale:
            print(f"  {s}")
        print("\n`authoring.py lock --update` 로 갱신하고, 왜 바뀌었는지 커밋 메시지에 남긴다.")
        return 1
    print(f"lock 최신 — {lp}")
    return 0


def cmd_emit_legacy_registry(args) -> int:
    """`templates/registry.json` 을 spec + paths.json 에서 굽는다.

    왜 흡수하지 않고 굽는가: 이 파일을 읽는 기존 툴링(`formalize-output` 의 렌더 스크립트)이
    이미 돌아가고 있다. 흡수해 버리면 그 툴링을 같이 고쳐야 하고, 그러면 이관 범위가
    렌더 파이프라인까지 번진다. **생성물로 강등**하면 툴링은 무손상으로 살고
    진실은 spec 한 곳에만 있게 된다 — 이중 진실을 만들지 않는 값싼 방법이다.
    """
    pd = Path(args.project or ".").expanduser()
    sd = specs_dir(pd)
    if not sd.is_dir():
        print(f"spec 이 없다: {sd}", file=sys.stderr)
        return 2
    paths_file = sd.parent / "paths.json"
    paths = json.loads(paths_file.read_text(encoding="utf-8")) if paths_file.exists() else {}
    templates = paths.get("templates", {})
    dirs = paths.get("dirs", {})
    positions = paths.get("positions", [])

    docs: dict = {}
    for d in sorted(sd.glob("*/")):
        try:
            s, _ = load_spec(d.name, pd)
        except Exception:
            continue
        tmpl = s.get("template", {})
        formats: dict = {}
        for out in tmpl.get("outputs", []):
            fmt = out.get("format")
            if not fmt:
                continue
            ref = out.get("template_ref") or tmpl.get("template_ref")
            entry = {"template": templates.get(ref), "kind": out.get("kind") or tmpl.get("kind")}
            if out.get("page_limit") is not None:
                entry["page_limit"] = out["page_limit"]
            if out.get("slides"):
                entry["slides"] = out["slides"]
            # 기존 파일의 키 이름을 유지한다 — 읽는 쪽을 고치지 않기 위해서다.
            formats["ppt" if fmt == "pptx" else fmt] = entry
        per_pos = any(o.get("per_position") for o in tmpl.get("outputs", []))
        ext = "{md,mdx}" if tmpl.get("kind") == "dual-format" or s["id"] == "포트폴리오" else "md"
        entry = {
            "_comment": f"authoring-kit spec '{s['id']}' 에서 생성됨. 직접 고치지 마라 — "
                        f"spec 을 고치고 `authoring.py emit-legacy-registry` 를 다시 돌린다.",
            "per_position": per_pos or None,
            "positions": positions if per_pos else None,
            "formats": formats,
        }
        if dirs.get("set") and per_pos:
            entry["set_glob"] = f"{dirs['set']}/{s['id']}.{ext}"
        docs[s["id"]] = {k: v for k, v in entry.items() if v is not None}

    out = {
        "_comment": "**생성물이다. 직접 고치지 마라.** authoring-kit 의 spec 과 paths.json 에서 "
                    "`authoring.py emit-legacy-registry` 로 굽는다. 진실은 "
                    ".claude/authoring/specs/*/spec.json 에 있다.",
        "_generated_from": {"specs": sorted(docs), "paths": str(paths_file.name)},
        "positions": positions,
        "output_pattern": paths.get("output_pattern",
                                    f"{dirs.get('output', '04_format')}/{{purpose}}/{{doc}}_v*.{{ext}}"),
        "docs": docs,
    }
    dest = Path(args.out).expanduser() if args.out else (
        (Path(_git(pd, "rev-parse", "--show-toplevel") or pd)) / "templates" / "registry.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{dest}")
    print(f"  문서 {len(docs)}개 · 직무 {len(positions)}개")
    missing = [f"{d}/{f}" for d, v in docs.items() for f, e in v.get("formats", {}).items()
               if not e.get("template")]
    if missing:
        print(f"  ! 템플릿 경로가 해소되지 않은 항목: {missing}")
        print(f"    paths.json 의 templates 에 키를 추가하라")
        return 1
    return 0


def cmd_path(args) -> int:
    if args.scope == "principles":
        print(principles_dir())
    elif args.scope == "specs":
        print(specs_dir(Path(args.project_dir or ".").expanduser()))
    else:
        print(voices_dir())
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("status"); p.add_argument("project_dir", nargs="?"); p.set_defaults(func=cmd_status)

    p = sub.add_parser("list"); p.add_argument("what", choices=["voices", "specs"])
    p.add_argument("project_dir", nargs="?"); p.set_defaults(func=cmd_list)

    p = sub.add_parser("show"); p.add_argument("kind", choices=["voice", "spec"]); p.add_argument("id")
    p.add_argument("--project", dest="project_dir"); p.set_defaults(func=cmd_show)

    p = sub.add_parser("resolve")
    p.add_argument("--voice", required=True); p.add_argument("--spec")
    p.add_argument("--project"); p.add_argument("--out")
    p.add_argument("--profile", choices=["main", "worker"], default="worker",
                   help="main=요약(메인 스레드용) · worker=전문(집필·채점 에이전트용)")
    p.add_argument("--frozen", action="store_true",
                   help="lock 과 어긋나면 집필하지 않고 exit 1 (CI·재현성 게이트)")
    p.set_defaults(func=cmd_resolve)

    p = sub.add_parser("validate")
    p.add_argument("--voice"); p.add_argument("--spec"); p.add_argument("--all", action="store_true")
    p.add_argument("--project"); p.set_defaults(func=cmd_validate)

    p = sub.add_parser("lock", help="규칙 조합을 프로젝트에 고정 / 어긋났는지 확인")
    p.add_argument("--update", action="store_true", help="현재 상태로 갱신")
    p.add_argument("--project")
    p.set_defaults(func=cmd_lock)

    p = sub.add_parser("emit-legacy-registry", help="spec + paths.json 에서 구 registry 를 굽는다")
    p.add_argument("--project"); p.add_argument("--out")
    p.set_defaults(func=cmd_emit_legacy_registry)

    p = sub.add_parser("path")
    p.add_argument("--scope", choices=["voices", "specs", "principles"], default="voices")
    p.add_argument("project_dir", nargs="?"); p.set_defaults(func=cmd_path)

    args = ap.parse_args()
    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
