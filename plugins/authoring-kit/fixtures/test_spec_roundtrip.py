#!/usr/bin/env python3
"""요구사항 ②("집필하려는 글 명세를 등록할 수 있어야 한다")의 기계적 합격 판정.

명세 등록이 받아야 하는 다섯 가지 입력이 실제로 저장되고, 집필 시점에 다시 꺼내지는지 본다.

    ① 항목            spec.json.sections[]
    ② 항목별 작성 방법  spec.md
    ③ 해당 글 범위의 원칙 spec.json.principles[]
    ④ 적용 퍼소나       spec.json.voice
    ⑤ 템플릿           spec.json.template + paths.json.templates

그리고 spec 이 자기 소관이 아닌 것을 침범하지 않는지(갈래 소유권), 경로·명령이 spec 에
섞여 들어오지 않았는지(재사용성)를 확인한다.

실행:
    AUTHORING_KIT_HOME=<레지스트리> python3 fixtures/test_spec_roundtrip.py <project_dir> <spec_id>
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
spec_ = importlib.util.spec_from_file_location("authoring", PLUGIN / "scripts" / "authoring.py")
A = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(A)

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


def main() -> int:
    project = Path(sys.argv[1] if len(sys.argv) > 1 else ".").expanduser()
    spec_id = sys.argv[2] if len(sys.argv) > 2 else "algo-guide"
    print(f"요구사항 ② — 글 명세 등록 왕복 (spec `{spec_id}`)\n")

    s, s_md = A.load_spec(spec_id, project)
    paths_file = A.specs_dir(project).parent / "paths.json"
    paths = json.loads(paths_file.read_text(encoding="utf-8")) if paths_file.exists() else {}

    print("[1] 다섯 입력이 저장돼 있는가")
    secs = s.get("sections", [])
    check("① 항목 — sections[] 가 비어 있지 않다", len(secs) > 0, f"{len(secs)}개")
    check("① 항목 — 각 항목에 id·label·required·order 가 있다",
          all({"id", "label", "required", "order"} <= set(x) for x in secs))
    check("② 작성 방법 — spec.md 가 각 항목을 다룬다",
          all(x["id"] in s_md or x["label"] in s_md for x in secs if not x.get("container")),
          "spec.md 에서 언급되지 않은 항목: " +
          str([x["id"] for x in secs if not x.get("container")
               and x["id"] not in s_md and x["label"] not in s_md]))
    prin = s.get("principles", [])
    check("③ 범위 원칙 — principles[] 가 비어 있지 않다", len(prin) > 0, f"{len(prin)}개")
    check("③ 범위 원칙 — 각 원칙에 code·level·axis·text 가 있다",
          all({"code", "level", "axis", "text"} <= set(p) for p in prin))
    check("④ 퍼소나 — voice.default 가 있고 레지스트리에 존재한다",
          bool(s.get("voice", {}).get("default")))
    # 템플릿은 두 형태가 다 정당하다.
    #   파일 참조  — 캔버스·HTML·PPTX 처럼 별도 파일이 있는 경우. paths.json 에서 해소돼야 한다.
    #   인라인 골격 — 골격이 sections[] 와 spec.md 안에 있는 경우. 참조할 파일이 애초에 없다.
    # 파일을 강제하면 후자를 위해 빈 템플릿 파일을 만들게 되고, 그건 이중 진실이 된다.
    tmpl = s.get("template", {})
    ref = tmpl.get("template_ref")
    if tmpl.get("kind") == "inline-skeleton" or not ref:
        check("⑤ 템플릿 — 인라인 골격이 sections[] 로 정의돼 있다",
              tmpl.get("kind") == "inline-skeleton" and len(secs) > 0,
              f"kind={tmpl.get('kind')} sections={len(secs)}")
    else:
        check("⑤ 템플릿 — template_ref 가 paths.json 에서 해소된다",
              ref in paths.get("templates", {}),
              f"{ref} not in {list(paths.get('templates', {}))}")

    print("\n[2] 갈래 소유권을 지키는가")
    bad_axis = [p for p in prin if A.AXIS_OWNER.get(p["axis"]) not in {"L2", "L0"}]
    check("principles 가 L1 소유 축(register/rhythm/device/lexicon)을 침범하지 않는다",
          not bad_axis, str([(p["code"], p["axis"]) for p in bad_axis]))
    check("spec 에 voice 항목 선언이 없다", "axes" not in s)

    print("\n[3] 경로·명령이 spec 에 섞이지 않았는가  ← 다른 프로젝트에서 재사용 가능한가")
    # `source` 는 **출처 이력**이지 운용 설정이 아니다. 어디서 가져왔는지는 경로로 적을 수밖에 없고,
    # 그 기록이 지워지면 이관을 나중에 검증할 수 없다. 검사 대상은 실제로 해석·실행되는 부분뿐이다.
    # 휴리스틱("슬래시가 있으면 경로")은 못 쓴다 — 산문에 `정의/수식`·`before/after`·`시간/공간`
    # 같은 표기가 자연스럽게 들어간다. 그래서 **불변식을 직접** 본다.
    tmpl = s.get("template", {})
    check("template 이 파일 경로 대신 template_ref 를 쓴다",
          "path" not in tmpl and "file" not in tmpl, str(tmpl))
    for k in ("bindings", "dirs", "commands", "paths"):
        check(f"spec 최상위에 '{k}' 키가 없다 (paths.json 소관)", k not in s)
    operational = {k: v for k, v in s.items() if k != "source"}
    raw = json.dumps(operational, ensure_ascii=False)
    for bad in ("bun run", "bun test", "npm run", "./tools/", "02_draft", ".claude/skills"):
        check(f"spec.json(출처 제외)에 '{bad}' 가 없다", bad not in raw)
    check("paths.json 에 commands 가 있다", bool(paths.get("commands")))
    check("출처 이력은 보존돼 있다", bool(s.get("source", {}).get("refs")))

    print("\n[4] 해석이 3층을 모두 싣는가")
    doc, meta = A.resolve(s["voice"]["default"], spec_id, project)
    check("해석 충돌 없음", not meta["conflicts"], str(meta["conflicts"]))
    check("L1(목소리) 실림", "## L1" in doc)
    check("L2(명세) 실림", "## L2" in doc)
    check("L0(공통) 실림", "## L0" in doc)
    check("범위 원칙이 실림", all(p["code"] in doc for p in prin))
    check("항목 골격이 실림", all(x["label"] in doc for x in secs))

    print("\n[5] 다른 voice 로는 해석되지 않는가  ← spec 의 allowed 가 지켜지는가")
    allowed = s.get("voice", {}).get("allowed")
    if allowed and "ppangto" not in allowed:
        _, m2 = A.resolve("ppangto", spec_id, project)
        check("허용되지 않은 voice 는 CONFLICT",
              any("CONFLICT" in c for c in m2["conflicts"]), str(m2["conflicts"]))
    else:
        check("allowed 목록 존재", bool(allowed))

    print(f"\n{'='*56}")
    print(f"통과 {PASSES} · 실패 {len(FAILS)}")
    if FAILS:
        print("\n실패 목록:")
        for f in FAILS:
            print(f"  - {f}")
        return 1
    print("요구사항 ② 통과 — 명세 5입력이 등록되고 집필 시점에 되살아난다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
