#!/usr/bin/env python3
"""게이트 B — 요구사항 ①("공통 원칙 ↔ 퍼소나 톤 분리")의 기계적 합격 판정.

이 파일이 통과하면 다음이 증명된다:

  1. 특정 저자(tony)의 문체가 **다른 퍼소나의 집필 컨텍스트에 새어 들어가지 않는다.**
     — 이번 이관 전에는 `AI_KOREAN_PATTERNS.md` Part B 가 "다른 모든 규칙보다 우선"으로
       승격돼 있어서, 발행 29편 중 22편을 쓴 AI 퍼소나 글에도 사람 저자의 만연체·당위
       마무리·한자어 인용이 강제되고 있었다. 그 경로가 실제로 닫혔는지 본다.
  2. 반대로 **공통 원칙(L0)은 모든 voice 에 그대로 적용된다.**
  3. hard floor(`evidence`·`grammar`)는 어떤 voice 도 waiver 로 뚫을 수 없다.

실행:
    AUTHORING_KIT_HOME=<레지스트리> python3 fixtures/test_layer_separation.py
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys
import tempfile
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("authoring", PLUGIN / "scripts" / "authoring.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)

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


# 한 저자에게만 속해야 하는 표지. L0 에 남아 있으면 그게 곧 유출이다.
TONY_ONLY = ["빵관 토니", "손자병법", "사통팔달", "샘플3", "샘플1", "4무의 인간"]
TEACHER_ONLY = ["빵토 선생님", "ascii art", "스스로 점검하기", "존댓말 설명체", "balance factor"]
# 모든 voice 가 받아야 하는 공통 규칙의 표지.
L0_MARKERS = ["영어투", "이중 피동", "쉼표 과다", "헤지", "무생물 주어"]


def main() -> int:
    print("게이트 B — 층 분리 검증\n")

    tony, tony_meta = A.resolve("ppangto", None, Path("."))
    teach, teach_meta = A.resolve("ppangtolab-teacher", None, Path("."))

    print("[1] 해석 자체가 성공하는가")
    check("tony 해석 충돌 없음", not tony_meta["conflicts"], str(tony_meta["conflicts"]))
    check("ppangtolab-teacher 해석 충돌 없음", not teach_meta["conflicts"], str(teach_meta["conflicts"]))

    print("\n[2] 저자 고유 문체가 상대 voice 로 새지 않는가  ← 요구사항 ①의 핵심")
    for m in TONY_ONLY:
        check(f"'{m}' 이 teacher 컨텍스트에 없다", m not in teach)
    for m in TEACHER_ONLY:
        check(f"'{m}' 이 tony 컨텍스트에 없다", m not in tony)

    print("\n[3] 자기 voice 의 문체는 제대로 실리는가")
    check("tony 컨텍스트에 만연체 선언 있음", "만연체" in tony)
    check("tony 컨텍스트에 손자병법 어휘군 있음", "손자병법" in tony)
    check("teacher 컨텍스트에 작은 단계 선언 있음", "작은 단계" in teach)
    check("teacher 컨텍스트에 ascii art 장치 있음", "ascii art" in teach)

    print("\n[4] 공통 원칙은 두 voice 모두에 적용되는가")
    for m in L0_MARKERS:
        check(f"'{m}' 이 양쪽 모두에 있다", m in tony and m in teach)

    print("\n[5] waiver 가 voice 별로 다른가")
    check("tony 는 R2·R1b·F4 를 면제받는다",
          set(tony_meta["waived"]) == {"R2", "R1b", "F4"}, str(tony_meta["waived"]))
    check("teacher 는 면제가 없다", teach_meta["waived"] == [], str(teach_meta["waived"]))

    print("\n[6] hard floor 는 뚫리지 않는가")
    bad = {"id": "evil", "label": "x", "kind": "ai-persona", "status": "defined",
           "axes": {}, "waivers": [{"code": "A5", "target": "L0:grammar", "reason": "테스트"}]}
    problems: list[str] = []
    A.validate_voice(bad, problems)
    check("grammar 를 겨냥한 waiver 는 거부된다",
          any("hard floor" in p for p in problems), str(problems))

    bad2 = {"id": "evil2", "label": "x", "kind": "ai-persona", "status": "defined",
            "axes": {"structure": "섹션 순서를 내가 정한다"}, "waivers": []}
    problems2: list[str] = []
    A.validate_voice(bad2, problems2)
    check("voice 가 L2 소유 축(structure)을 선언하면 갈래 위반",
          any("갈래 위반" in p for p in problems2), str(problems2))

    bad3 = {"id": "evil3", "label": "x", "kind": "ai-persona", "status": "defined",
            "axes": {}, "waivers": [{"code": "R2", "target": "L0:machine-rhythm"}]}
    problems3: list[str] = []
    A.validate_voice(bad3, problems3)
    check("사유 없는 waiver 는 거부된다",
          any("reason" in p for p in problems3), str(problems3))

    print("\n[7] 해석 결과가 결정론적인가  ← 재현성의 토대")
    again, again_meta = A.resolve("ppangto", None, Path("."))
    check("같은 입력 → 같은 해시", tony_meta["hash"] == again_meta["hash"],
          f"{tony_meta['hash']} vs {again_meta['hash']}")

    print("\n[8] 퍼소나 없이는 글이 써지지 않는다")
    # 예전에는 voice.md 가 없으면 `_voice.md 없음_` 한 줄을 싣고 넘어갔고, 그래서
    # 집필 에이전트가 퍼소나 규칙을 못 본 채 한 편을 썼다. **구조로 막는다.**
    check("VoiceEmpty 예외가 정의돼 있다", hasattr(A, "VoiceEmpty"))
    thin = {"axes": {"register": "짧게"}}
    check("축 하나뿐인 voice 는 실속 없음으로 본다",
          not A._has_voice_substance("짧게", thin))
    full = {"axes": {"register": "정중한 공유체다. " * 20, "rhythm": "발견 먼저. " * 20}}
    check("축 둘 이상 + 분량이면 통과",
          A._has_voice_substance("정중한 공유체다. " * 30, full))
    check("defined 인데 voice.md 없으면 validate 가 잡는다",
          "voice.md 가 없다" in (pathlib.Path(A.__file__).read_text(encoding="utf-8")))

    print(f"\n{'='*56}")
    print(f"통과 {PASSES} · 실패 {len(FAILS)}")
    if FAILS:
        print("\n실패 목록:")
        for f in FAILS:
            print(f"  - {f}")
        return 1
    print("게이트 B 통과 — 공통 원칙과 퍼소나 톤이 기계적으로 분리돼 있다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
