#!/usr/bin/env python3
"""문체 스캐너 — 세는 단위 검증.

여기 모인 케이스는 전부 **실전에서 오탐이 났던 것**이다. 예외를 넓히다 탐지력을 죽이는 일이
잦아서, 오탐 케이스와 **진짜로 잡아야 하는 케이스를 함께** 둔다. 한쪽만 통과하면 실패다.

실행:  python3 fixtures/test_scanner.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("scan", PLUGIN / "scripts" / "scan_ai_style.py")
S = importlib.util.module_from_spec(spec)
sys.modules["scan"] = S
spec.loader.exec_module(S)

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


SIM_DOC = """본문 첫 문단입니다. 짧게 씁니다.

export const steps = [
  { title: "정렬 후 출발 — 첫 걸음", detail: "창을 연다. 값을 센다. 결과를 담는다." },
  { title: "두 번째 — 이동", detail: "포인터를 민다. 개수를 갱신한다. 답을 적는다." },
];

<AlgorithmSimulation steps={steps} />

여기는 진짜 산문입니다. 이 문장은 세어야 합니다.
"""


def main() -> int:
    print("문체 스캐너 — 세는 단위\n")

    print("[1] MDX export 블록은 데이터지 산문이 아니다")
    # 명세가 강제하는 산출물(선언형 steps)이 문체 규칙(P2 줄표·R1b 어미)에 걸리면,
    # 집필자가 데이터의 문자열을 문체 때문에 고치게 된다. 골든셋 회귀에서 두 번 나왔다.
    stripped = S.strip_non_prose(SIM_DOC)
    check("export 블록 본문이 제거된다", "detail:" not in stripped)
    check("닫는 괄호 줄도 남지 않는다", "];" not in stripped, repr(stripped[:80]))
    check("앞뒤 산문은 살아남는다",
          "본문 첫 문단" in stripped and "진짜 산문" in stripped)
    r = S.scan(SIM_DOC)
    check("steps 의 줄표가 P2 로 잡히지 않는다",
          "P2" not in {f["code"] for f in r["findings"]},
          str([f["code"] for f in r["findings"]]))

    print("\n[2] 그래도 진짜 증상은 잡아야 한다")
    dash = ("한 문단 안에서 부연을 — 이렇게 — 두 번 넣고, 또 한 번 — 이렇게 — 더 넣습니다. "
            "세 번째 부연도 — 여기 — 붙입니다.\n")
    check("본문의 줄표 남용은 P2 로 잡힌다",
          "P2" in {f["code"] for f in S.scan(dash)["findings"]},
          str([f["code"] for f in S.scan(dash)["findings"]]))

    # 주의: 짧은 명사구를 쉼표로 이으면 `is_enumeration()` 예외에 걸려 P1 이 안 난다(설계대로).
    # 진짜 P1 은 **절이 길게 이어지는** 문장이다. 테스트 문장을 그렇게 써야 한다.
    comma = ("규모를 키우면, 앞서 본 것처럼, 겹치는 구간을 다시 세는 비용이, "
             "전체를 지배하게 되고, 결국 제한 시간을 넘깁니다.\n")
    check("쉼표 과다는 P1 로 잡힌다",
          "P1" in {f["code"] for f in S.scan(comma)["findings"]},
          str([f["code"] for f in S.scan(comma)["findings"]]))

    print("\n[3] 나열·병렬은 쉼표 과다가 아니다")
    enum = "관찰할 것 — link LED, 광 power, cable 규격, CRC error.\n"
    check("항목 나열은 P1 에서 제외된다",
          "P1" not in {f["code"] for f in S.scan(enum)["findings"]},
          str([f["code"] for f in S.scan(enum)["findings"]]))

    print("\n[4] voice 면제가 등급에 반영된다")
    r_none = S.scan(comma, set())
    r_waived = S.scan(comma, {"P1"})
    check("면제하면 S1 카운트에서 빠진다", r_waived["s1"] < r_none["s1"],
          f"{r_none['s1']} → {r_waived['s1']}")
    check("면제해도 적발 목록에는 남는다",
          any("면제됨" in f["label"] for f in r_waived["findings"]))

    print("\n[5] 마커 주석과 숫자 쉼표는 문장이 아니다 (code_test KAN-063)")
    markers = "본문 문단입니다.\n\n<!--viz:walk--> <!--fig:walk-->\n\n다음 문단입니다.\n"
    check("마커 주석 둘은 P4 로 잡히지 않는다",
          "P4" not in {f["code"] for f in S.scan(markers)["findings"]},
          str([f["code"] for f in S.scan(markers)["findings"]]))
    bang = "정말 빠릅니다! 놀랍게도 답이 맞습니다!\n"
    check("본문의 느낌표 둘은 여전히 P4 로 잡힌다",
          "P4" in {f["code"] for f in S.scan(bang)["findings"]},
          str([f["code"] for f in S.scan(bang)["findings"]]))
    nums = "칸 1,000 개면 1,000,000 번이고 칸 2,000 개면 4,000,000 번입니다.\n"
    check("천 단위 쉼표는 P1 으로 세지 않는다",
          "P1" not in {f["code"] for f in S.scan(nums)["findings"]},
          str([f["code"] for f in S.scan(nums)["findings"]]))
    check("숫자 사이가 아닌 쉼표는 여전히 센다", S.commas_outside_parens("1, 2, 3") == 2)

    print(f"\n{'='*56}")
    print(f"통과 {PASSES} · 실패 {len(FAILS)}")
    if FAILS:
        print("\n실패 목록:")
        for f in FAILS:
            print(f"  - {f}")
        return 1
    print("스캐너 통과.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
