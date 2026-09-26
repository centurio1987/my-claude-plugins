#!/usr/bin/env python3
"""문체 설정 — 전역 → voice 계승, 가중치·필터, 면제 규칙, 스캐너 이관, 편집기 API.

레지스트리를 임시 디렉토리에 새로 만들어 돈다. 사용자 레지스트리를 건드리지 않고, 없어도 돈다.

실행:  python3 fixtures/test_style.py
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import threading
import urllib.request
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
TMP = Path(tempfile.mkdtemp(prefix="authoring-style-"))
os.environ["AUTHORING_KIT_HOME"] = str(TMP)
sys.path.insert(0, str(PLUGIN / "scripts"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, PLUGIN / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


SR = _load("style_registry")
SCAN = _load("scan_ai_style")
LEX = _load("scan_lexicon")
A = _load("authoring")
SRV = _load("style_server")

FAILS: list[str] = []
PASSES = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASSES
    if ok:
        PASSES += 1
        print(f"  ok   {name}")
    else:
        FAILS.append(f"{name}{(' — ' + detail) if detail else ''}")
        print(f"  FAIL {name}{(' — ' + detail) if detail else ''}")


def make_voice(vid: str, usage: str = "generate") -> None:
    d = TMP / "voices" / vid
    d.mkdir(parents=True, exist_ok=True)
    (d / "voice.json").write_text(json.dumps({
        "$schema": "authoring-kit/voice@1", "schema_version": 1, "id": vid, "label": vid,
        "kind": "ai-persona", "usage": usage, "status": "defined", "source": {"origin": "test"},
        "axes": {"register": "정중한 설명체다. " * 8, "rhythm": "작은 단계로 끊는다. " * 8,
                 "device": ["self-check-question"], "lexicon": "쉬운 말."},
        "waivers": [], "forbid": ["반말"]}, ensure_ascii=False), encoding="utf-8")
    (d / "voice.md").write_text(f"# {vid}\n\n" + "문체 규칙 — 정중한 설명체로 쓴다. 예: 이 값은 0부터 셉니다.\n" * 8,
                                encoding="utf-8")


def write_layer(scope: str, layer: dict) -> None:
    p = SR.layer_path(scope)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(layer, ensure_ascii=False), encoding="utf-8")


def item(eff: dict, iid: str) -> dict:
    return next(x for x in eff["items"] if x["id"] == iid)


# 이관 전 scan_ai_style.py 에 하드코딩돼 있던 목록. 카탈로그로 옮긴 뒤에도 **같은 말을 같은 코드로** 세야 한다.
LEGACY = {
    "W1": ["중요한 역할", "핵심적인 역할", "필수적입니다", "필수적인 요소"],
    "W2": ["시사하는 바", "주목할 만", "의미가 있습니다", "중요한 의미를"],
    "W3": ["살펴보겠습니다", "알아보겠습니다", "정리해 보겠습니다", "알아봅시다", "살펴봅시다"],
    "W4": ["에 있어서", "함에 있어", "에 있어 "],
    "W5": ["다양한", "여러 가지", "수많은", "많은 경우"],
    "W6": ["라고 할 수 있", "라고 볼 수 있", "이라 할 수 있"],
    "W7": ["효율적으로", "효과적으로", "원활하게", "손쉽게"],
    "W8": ["점점 더 중요", "필수가 되었", "빼놓을 수 없는", "화두가 되고 있"],
    "H1": ["다소", "어느 정도", "비교적", "대체로", "일반적으로", "보통", "아마도", "경우가 많",
           "일 수 있습니다", "될 수 있습니다", "것 같습니다", "로 보입니다", "인 듯합니다", "수도 있습니다"],
    "H2": ["인 것 같습니다", "것 같습니다", "인 듯합니다", "로 보입니다", "수도 있습니다", "일 수 있습니다", "지 않을까 합니다"],
    "H3": ["일반적으로", "대체로", "보통", "흔히"],
    "D1": ["하지만", "그러나", "또한", "따라서", "그리고", "즉", "한편", "이처럼"],
    "D2": ["기본적으로", "사실상"],
    "D3": ["첫째", "둘째", "셋째"],
    "D4": ["앞서 언급", "위에서 살펴본", "앞에서 설명한"],
    "D6": ["무너지지", "무너뜨리", "무너집", "버티는 힘", "버텨냅", "걷어내겠", "걷어냅", "깨고 시작", "깨지는 문장",
           "속이지", "쥐여 주", "쥐여줍", "밀어 올리", "걸터앉", "짓밟", "맞서 싸", "때려눕", "굴복"],
}


def main() -> int:
    print("문체 설정 — 계승 · 가중치 · 면제 · 스캐너 · 편집기\n")

    print("[1] 기본 카탈로그와 분류 체계")
    check("카탈로그 정합", SR.validate_catalog() == [], str(SR.validate_catalog()[:3]))
    check("L1 축 상수가 authoring.py 와 같다",
          set(SR.L1_AXES) == {k for k, v in A.AXIS_OWNER.items() if v == "L1"})
    check("hard floor·면제 상수가 authoring.py 와 같다",
          SR.HARD_FLOOR == A.HARD_FLOOR and SR.WAIVABLE == A.WAIVABLE)
    tax = SR.load_taxonomy()["categories"]
    leaves = [c for c in tax if c.get("parent")]
    check("정성 말단이 전부 L1 축 하나에 묶인다", all(c.get("axis") in SR.L1_AXES for c in leaves))
    check("정성 말단마다 정의·판정 질문·지시 예시·근거가 있다",
          all(c.get("definition") and c.get("questions") and c.get("templates") and c.get("basis") for c in leaves))
    check("정성 판정 규칙이 기계 장치를 금한다",
          any("스크립트" in r and "만들" in r for r in SR.load_taxonomy()["judging"]["rules"]))
    cat = SR.load_catalog()
    check("형식 분류가 5언을 모두 갖는다",
          {"nominal", "predicate", "modifier", "relational", "interjection"} <= {c["id"] for c in cat["categories"]})
    check("기능 태그에 Hyland 메타담화 10갈래가 있다",
          {"transition", "frame-marker", "endophoric", "evidential", "code-gloss",
           "hedge", "booster", "attitude", "self-mention", "engagement"} <= {f["id"] for f in cat["functions"]})

    print("\n[2] L0 스캐너 어휘 이관 — 하드코딩 목록과 같은가")
    lists = SR.l0_lists()
    for code, legacy in LEGACY.items():
        got = []
        for x in lists.get(code, []):
            got += [f for f in x.get("forms", []) if f not in got]
        check(f"{code} 목록 동등", sorted(got) == sorted(legacy), f"{sorted(set(got) ^ set(legacy))}")
    check("D7~D11 은 정규식 항목으로 있다", all(SCAN.regex_items(c) for c in ("D7", "D8", "D9", "D10", "D11")))
    r = SCAN.scan("이 규칙이 이깁니다. 두 축을 교차합니다. 요금이 비쌉니다. 이 쿼리는 비싸다.")
    codes = {f["code"] for f in r["findings"]}
    check("D7·D11 은 잡고 예외 문맥(축 교차·요금)은 뺀다",
          "D7" in codes and "D11" in codes and "D9" not in codes, str(codes))

    print("\n[3] 계승 — 기본값 → 전역 → voice")
    make_voice("alpha")
    make_voice("beta", usage="preserve")
    write_layer("global", {"lexicon": {
        "overrides": {"adv.degree.1": {"weight": -2}, "adv.degree.2": {"weight": -1}},
        "categories": {"interjection": {"enabled": False}, "modifier.adverb": {"check": {"stack": 3}}},
        "add": [{"id": "g.eomcheongnage", "category": "modifier.adverb.degree", "forms": ["엄청나게"], "weight": -3}]},
        "directives": {"add": [{"id": "g.certainty", "category": "stance.certainty", "text": "확신도는 근거 수준에 맞춘다.",
                                "gate": {"enabled": True, "level": "SHOULD"}}]}})
    write_layer("voice:alpha", {"lexicon": {
        "overrides": {"adv.degree.2": {"weight": 1}, "d1.hajiman": {"weight": 2, "reason": "문단을 하지만으로 여는 게 색이다"}},
        "add": [{"id": "v.gureonikka", "category": "modifier.adverb.conjunctive", "forms": ["그러니까"], "weight": 3}]},
        "directives": {"overrides": {"g.certainty": {"gate": {"level": "MUST"}}},
                       "add": [{"id": "v.self-check", "category": "engage.question", "text": "절 끝에 점검 질문을 둔다."}]}})
    g, a, b = SR.effective(None), SR.effective("alpha"), SR.effective("beta")
    check("전역 재정의가 전역 유효값에 보인다", item(g, "adv.degree.1")["weight"] == -2 and item(g, "adv.degree.1")["weight_from"] == "global")
    check("voice 가 전역을 계승한다", item(b, "adv.degree.1")["weight"] == -2 and item(b, "adv.degree.1")["weight_from"] == "global")
    check("voice 가 전역을 덮는다", item(a, "adv.degree.2")["weight"] == 1 and item(a, "adv.degree.2")["weight_from"] == "voice")
    check("전역이 추가한 항목을 voice 가 물려받는다", any(x["id"] == "g.eomcheongnage" for x in b["items"]))
    check("voice 가 추가한 항목은 그 voice 에만 있다",
          any(x["id"] == "v.gureonikka" for x in a["items"]) and not any(x["id"] == "v.gureonikka" for x in b["items"]))
    check("분류를 끄면 하위 항목까지 필터링된다", not item(a, "intj.spoken")["active"])
    check("분류 점검 기준값을 부모 층에서 덮으면 자식에게는 안 번진다(키 단위, 그 분류만)",
          next(c for c in a["categories"] if c["id"] == "modifier.adverb")["check"].get("stack") == 3
          and next(c for c in a["categories"] if c["id"] == "modifier.adverb.modal")["check"].get("stack") == 2)
    da = {d["id"]: d for d in a["directives"]}
    check("정성 지시도 계승하고 voice 가 게이트 등급만 덮는다",
          da["g.certainty"]["gate"] == {"enabled": True, "level": "MUST"} and da["g.certainty"]["overridden_by"] == "voice")
    check("정성 지시의 축은 분류가 정한다", da["v.self-check"]["axis"] == "device")
    check("다른 voice 에는 새지 않는다", "v.self-check" not in {d["id"] for d in b["directives"]})

    print("\n[4] 검증 — 저장 전에 막는다")
    def problems(scope: str, layer: dict) -> list[str]:
        base = {"global": SR.load_layer("global")} if scope != "global" else None
        return SR.validate_layer(scope, layer, base_layers=base)
    bad_cases = {
        "hard floor 가중치 상향": {"lexicon": {"overrides": {"passive.double": {"weight": -1}}}},
        "hard floor 항목 끄기": {"lexicon": {"overrides": {"rel.cmp.about.1": {"enabled": False}}}},
        "hard floor 가 든 분류 끄기": {"lexicon": {"categories": {"predicate.passive": {"enabled": False}}}},
        "사유 없는 L0 어휘 면제(양수)": {"lexicon": {"overrides": {"w5.1": {"weight": 1}}}},
        "사유 없는 L0 어휘 면제(끄기)": {"lexicon": {"overrides": {"w5.1": {"enabled": False}}}},
        "범위 밖 가중치": {"lexicon": {"overrides": {"adv.degree.3": {"weight": 4}}}},
        "불리언 가중치": {"lexicon": {"overrides": {"adv.degree.3": {"weight": True}}}},
        "없는 항목 덮기": {"lexicon": {"overrides": {"nope": {"weight": 1}}}},
        "기존 id 로 추가": {"lexicon": {"add": [{"id": "adv.degree.3", "category": "modifier.adverb.degree", "forms": ["x"]}]}},
        "깨진 정규식": {"lexicon": {"add": [{"id": "v.bad", "category": "phrase.cliche", "regex": "(("}]}},
        "사용자 항목이 L0 기원을 참칭": {"lexicon": {"add": [{"id": "v.l0", "category": "phrase.cliche", "forms": ["x"],
                                                     "l0": {"code": "W1", "axis": "machine-rhythm"}}]}},
        "분류 점검 음수": {"lexicon": {"categories": {"modifier.adverb.degree": {"check": {"density_per_1000": -1}}}}},
        "겹침 기준 소수": {"lexicon": {"categories": {"modifier.adverb.degree": {"check": {"stack": 1.5}}}}},
        "빈 지시문": {"directives": {"add": [{"id": "v.empty", "category": "stance.force", "text": "  "}]}},
        "없는 정성 분류": {"directives": {"add": [{"id": "v.x", "category": "structure.order", "text": "순서를 바꾼다"}]}},
        "게이트 등급 오타": {"directives": {"add": [{"id": "v.y", "category": "stance.force", "text": "단호하게",
                                              "gate": {"enabled": True, "level": "MAY"}}]}},
    }
    for name, layer in bad_cases.items():
        check(f"거부: {name}", bool(problems("voice:alpha", layer)))
    check("사유가 있는 L0 어휘 면제는 받는다",
          problems("voice:alpha", {"lexicon": {"overrides": {"w5.1": {"weight": 1, "reason": "나열이 이 voice 의 색"}}}}) == [])
    check("hard floor 가중치를 더 내리는 것은 받는다",
          problems("voice:alpha", {"lexicon": {"overrides": {"rel.cmp.about.1": {"weight": -3}}}}) == [])
    check("현재 레지스트리 전체 검증 통과", SR.validate_all() == [], str(SR.validate_all()[:3]))

    print("\n[5] 가중치 어휘 스캔")
    def lex(text: str, vid: str | None = "alpha") -> dict:
        return LEX.run(text, vid)
    r = lex("이 값은 엄청나게 큽니다. 다음 줄로 넘어갑니다.")
    check("금지(-3)는 1회부터 초과", any(x["id"] == "g.eomcheongnage" and x["verdict"] == "over" for x in r["over"]))
    r = lex("에 대해 말합니다. 에 대해 또 말합니다. 끝입니다.")
    check("절제(-1)는 최소 2회까지 허용", not any(x["id"] == "rel.cmp.about.1" for x in r["over"]))
    r = lex(("에 대해 말합니다. " * 3) + "끝입니다.")
    check("절제(-1) 허용량을 넘으면 적발", any(x["id"] == "rel.cmp.about.1" for x in r["over"]))
    long_text = "문장을 차례대로 씁니다. " * 80
    r = lex(long_text)
    check("표지(+3)를 한 번도 안 쓰면 경고하고 통과시키지 않는다",
          any(x["id"] == "v.gureonikka" for x in r["unused"]) and not r["pass"])
    r = lex("값이 바뀝니다 그러니까 다시 셉니다. " + long_text)
    check("문장 머리 모드는 문장 중간을 세지 않는다", any(x["id"] == "v.gureonikka" for x in r["unused"]))
    r = lex("그러니까 다시 셉니다. " + long_text)
    check("문장 머리에 오면 센다", not any(x["id"] == "v.gureonikka" for x in r["unused"]))
    r = lex("값을 셉니다. 값을 봅니다. 값이 큽니다요.", "beta")
    row = next((x for x in r["rows"] if x["id"] == "end.hapsyo"), None)
    check("문장 끝 모드는 점유율을 낸다", row is not None and row.get("share") == round(2 / 3, 3), str(row))
    r = lex("데이터의 처리의 효율의 향상입니다.")
    check("겹침은 등장 횟수로 센다('의' 3연쇄)",
          any(c["category"] == "relational.genitive" and c["kind"] == "stack" for c in r["category"]))
    r = lex("정말 좋습니다. 매우 큽니다.", "beta")
    check("밀도는 3회 미만이면 판정하지 않는다", not any(c["kind"] == "density" for c in r["category"]))
    check("L0 스캐너가 세는 항목은 가중치 스캔에서 빠진다",
          not any((x.get("l0") or {}).get("scanner") for x in lex("다양한 방법이 있습니다.")["rows"]))

    print("\n[6] L0 항목 단위 면제가 스캐너에 닿는가")
    doc = "하지만 첫 문단입니다.\n\n또한 둘째 문단입니다.\n\n따라서 셋째 문단입니다.\n"
    SCAN.LEX = SR.l0_lists()
    check("면제 전: D1 적발", "D1" in {f["code"] for f in SCAN.scan(doc)["findings"]})
    SCAN.load_voice_context("alpha")
    check("voice 가 '하지만'을 +2 로 올리면 D1 목록에서 빠진다", "D1" not in {f["code"] for f in SCAN.scan(doc)["findings"]})
    check("올린 어휘는 보호 목록에 오른다", "하지만" in SCAN.PROTECTED and "그러니까" in SCAN.PROTECTED)
    SCAN.load_voice_context("beta")
    check("다른 voice 에는 면제가 새지 않는다", "D1" in {f["code"] for f in SCAN.scan(doc)["findings"]})
    write_layer("voice:beta", {"lexicon": {"overrides": {"d1.hajiman": {"weight": 2}}}})   # 사유 없는 면제
    SCAN.load_voice_context("beta")
    check("검증에 실패한 설정은 스캐너가 적용하지 않는다(사유 없는 면제 차단)",
          "D1" in {f["code"] for f in SCAN.scan(doc)["findings"]})
    SR.layer_path("voice:beta").unlink()
    SCAN.LEX = SR.l0_lists()

    print("\n[7] 해석 결과에 실리는가")
    work, meta = A.resolve("alpha", None, Path("."), profile="worker")
    main_doc, _ = A.resolve("alpha", None, Path("."), profile="main")
    check("해석 충돌 없음", meta["conflicts"] == [], str(meta["conflicts"]))
    check("worker 에 가중치 대역이 실린다", "**금지 (-3)**" in work and "엄청나게" in work)
    check("worker 에 정성 지시와 게이트 판정 규칙이 실린다",
          "Q:g.certainty" in work and "스크립트·정규식·카운터를 만들거나 돌리지 않는다" in work)
    check("가중치 0 항목은 싣지 않는다", "추상·포괄 명사:" not in work)
    check("바뀌지 않은 L0 스캐너 항목은 싣지 않는다", "중요한 역할" not in work.split("## L0")[0])
    check("L0 항목 면제는 사유와 함께 실린다", "문단을 하지만으로 여는 게 색이다" in work)
    check("main 은 개수와 게이트 코드만", "Q:g.certainty" in main_doc and "**금지 (-3)**" not in main_doc)
    beta_doc, _ = A.resolve("beta", None, Path("."), profile="worker")
    check("preserve voice 는 지킬 색으로 렌더된다", "다듬을 때 지킬 색" in beta_doc)
    write_layer("voice:beta", {"lexicon": {"overrides": {"passive.double": {"weight": 0}}}})
    _, bad_meta = A.resolve("beta", None, Path("."), profile="worker")
    check("잘못된 voice 문체 설정은 해석 충돌로 올라온다", any("hard floor" in c for c in bad_meta["conflicts"]))
    SR.layer_path("voice:beta").unlink()

    print("\n[8] lock 이 문체 설정을 고정한다")
    lock = A.build_lock(TMP)
    check("lock 에 style 묶음이 있다", {"catalog/lexicon.json", "catalog/qualitative.json", "global/style.json"} <= set(lock["style"]))
    lp = A.lock_path(TMP)
    lp.parent.mkdir(parents=True, exist_ok=True)
    lp.write_text(json.dumps(lock, ensure_ascii=False), encoding="utf-8")
    check("바꾸기 전에는 어긋남 없음", A.lock_drift(TMP) == [], str(A.lock_drift(TMP)))
    gl = json.loads(SR.global_path().read_text(encoding="utf-8"))
    gl["lexicon"]["overrides"]["adv.degree.4"] = {"weight": -1}
    SR.global_path().write_text(json.dumps(gl, ensure_ascii=False), encoding="utf-8")
    check("전역 설정을 바꾸면 lock 이 안다", any("style/global/style.json" in d for d in A.lock_drift(TMP)))

    print("\n[9] 편집기 서버")
    srv = SRV.make_server("127.0.0.1", 0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"

    def call(method: str, path: str, body=None, header=True):
        req = urllib.request.Request(base + path, method=method,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"X-Authoring-Kit": "1"} if header else {})
        try:
            with urllib.request.urlopen(req) as res:
                return res.status, json.loads(res.read() or b"{}") if "json" in res.headers["Content-Type"] else res.read()
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")
    st, body = call("GET", "/")
    check("편집기 페이지를 준다", st == 200 and b"<title>" in body)
    st, body = call("GET", "/api/state")
    check("상태 API", st == 200 and {v["id"] for v in body["voices"]} == {"alpha", "beta"} and body["taxonomy"]["categories"])
    st, _ = call("PUT", "/api/layer?scope=global", {"layer": {}}, header=False)
    check("헤더 없는 쓰기는 403", st == 403)
    before = SR.global_path().read_text(encoding="utf-8")
    st, body = call("PUT", "/api/layer?scope=global", {"layer": {"lexicon": {"overrides": {"passive.double": {"weight": 0}}}}})
    check("검증 실패면 422 이고 파일을 건드리지 않는다",
          st == 422 and body["problems"] and SR.global_path().read_text(encoding="utf-8") == before)
    st, _ = call("GET", "/api/layer?scope=voice:../../etc")
    check("경로를 벗어나는 scope 는 거부", st == 400)
    st, _ = call("GET", "/api/layer?scope=voice:nobody")
    check("없는 voice 는 거부", st == 400)
    st, body = call("PUT", "/api/layer?scope=voice:beta",
                    {"layer": {"lexicon": {"overrides": {"adv.degree.5": {"weight": -3}, "adv.degree.6": {}}}}})
    saved = json.loads(SR.layer_path("voice:beta").read_text(encoding="utf-8"))
    check("저장은 차분만 남긴다(빈 재정의는 걷는다)",
          st == 200 and saved["lexicon"]["overrides"] == {"adv.degree.5": {"weight": -3}}, str(saved.get("lexicon")))
    st, body = call("POST", "/api/effective", {"scope": "voice:beta",
                                               "layer": {"lexicon": {"overrides": {"adv.degree.5": {"weight": 2}}}}})
    check("미리보기는 저장하지 않고 초안으로 계산한다",
          st == 200 and item(body["effective"], "adv.degree.5")["weight"] == 2
          and json.loads(SR.layer_path("voice:beta").read_text(encoding="utf-8"))["lexicon"]["overrides"]["adv.degree.5"]["weight"] == -3)
    st, body = call("POST", "/api/scan", {"scope": "voice:alpha", "text": doc + "\n이 값은 엄청나게 큽니다.\n"})
    check("시험 스캔은 어휘 스캔과 L0 등급을 함께 낸다(항목 면제 반영)",
          st == 200 and body["lexicon"]["forbidden_hits"] >= 1 and "D1" not in {f["code"] for f in body["l0"]["findings"]})
    st, body = call("POST", "/api/render", {"scope": "voice:alpha", "profile": "main"})
    check("미리보기 렌더", st == 200 and "정성 지시" in body["markdown"])

    print("\n[10] 정성 분류별 선택지")
    leaves = [c for c in SR.load_taxonomy()["categories"] if c.get("parent")]
    check("하위 분류마다 선택지가 있다", all(c.get("options") for c in leaves),
          str([c["id"] for c in leaves if not c.get("options")]))
    check("선택지는 스펙트럼 값과 지시 예시를 그대로 옮긴 것이다",
          all(len([o for o in c["options"] if o["group"] == "spectrum"]) == len(c.get("poles") or [])
              and [o["text"] for o in c["options"] if o["group"] == "rule"] == (c.get("templates") or []) for c in leaves))
    cg = SR.empty_layer()
    cg["directives"]["choices"] = {"tenor.formality": ["s3", "t1"], "tenor.speech-level": ["s2"]}
    check("선택이 검증을 통과한다", SR.validate_layer("global", cg) == [], str(SR.validate_layer("global", cg)))
    ceff = SR.effective(None, layers={"global": cg})
    cids = [d["id"] for d in ceff["directives"] if d.get("choice")]
    check("고른 선택지가 지시가 된다(축은 분류의 축)",
          cids == ["tenor.formality#s3", "tenor.formality#t1", "tenor.speech-level#s2"]
          and all(d["axis"] == "register" for d in ceff["directives"] if d.get("choice")), str(cids))
    cmd = SR.render(ceff)
    check("렌더에 고른 선택지 문장이 실린다", "격식도: ‘상담적’ 쪽으로 맞춘다." in cmd and "고른 선택지" in cmd)
    cv = SR.empty_layer()
    cv["directives"]["choices"] = {"tenor.formality": ["s5"], "tenor.speech-level": []}
    check("voice 선택이 검증을 통과한다", SR.validate_layer("voice:beta", cv, base_layers={"global": cg}) == [])
    cve = SR.effective("beta", layers={"global": cg, "voice:beta": cv})
    check("voice 는 분류 단위로 전역 선택을 대신하고, 빈 목록은 고르지 않음이다",
          [d["id"] for d in cve["directives"] if d.get("choice")] == ["tenor.formality#s5"]
          and cve["choices"]["tenor.formality"] == {"ids": ["s5"], "source": "voice", "overrides": "global"})
    cvi = SR.effective("beta", layers={"global": cg, "voice:beta": SR.empty_layer()})
    check("voice 가 안 고른 분류는 전역을 물려받는다",
          [d["id"] for d in cvi["directives"] if d.get("choice")] == cids)
    cb = SR.empty_layer()
    cb["directives"]["choices"] = {"tenor": ["s1"], "nope.x": [], "tenor.orality": "s1",
                                   "tenor.formality": ["s1", "s2", "zz", "t1", "t1"]}
    cbp = " | ".join(SR.validate_layer("global", cb))
    for frag in ("choices[tenor]: 알 수 없는", "choices[nope.x]: 알 수 없는", "선택지 id 의 목록",
                 "없는 선택지 ['zz']", "두 번 골랐다", "스펙트럼 선택지는 하나만"):
        check(f"잘못된 선택 거부 — {frag}", frag in cbp, cbp)
    check("선택이 없는 층은 저장 파일에 choices 키를 만들지 않는다, voice 의 빈 목록은 남긴다",
          "choices" not in SR.prune_layer(SR.empty_layer())["directives"]
          and SR.prune_layer(cv)["directives"]["choices"] == {"tenor.formality": ["s5"], "tenor.speech-level": []})
    st, body = call("PUT", "/api/layer?scope=global", {"layer": {"directives": {"choices": {"tenor.formality": ["s1", "s2"]}}}})
    check("서버가 스펙트럼 둘을 고른 저장을 422 로 거부", st == 422 and any("하나만" in p for p in body["problems"]))
    st, body = call("POST", "/api/effective", {"scope": "global", "layer": cg})
    check("유효값 API 가 고른 선택지를 준다", st == 200 and body["effective"]["choices"]["tenor.formality"]["ids"] == ["s3", "t1"])
    # 하나만 고르는 방향은 라디오 묶음이어야 한다 — 체크 상자로 그리면 여러 개 고를 수 있어 보인다(유저 지적, 2026-09-27).
    ui = (SR.PLUGIN_ROOT / "ui" / "style-editor.html").read_text(encoding="utf-8")
    check("편집기: 방향 선택지는 라디오, 규칙 선택지만 체크 상자",
          'type="radio" name="${esc(name)}" data-spec=' in ui and '"지정 안 함"' in ui
          and 'type="checkbox" data-opt=' in ui and "rule.map(row)" in ui and "spec.map(row)" not in ui)
    srv.shutdown()

    print(f"\n{'=' * 56}")
    print(f"통과 {PASSES} · 실패 {len(FAILS)}")
    if FAILS:
        print("\n실패 목록:")
        for f in FAILS:
            print(f"  - {f}")
        return 1
    print("문체 설정 통과.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
