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

    print("\n[6] K1 — 꼬리표를 서술어로 쓴 문장 (손으로 고친 기술 문서 한 편, 2026-11)")
    # 고치기 전 원고는 등급 A 였는데 `확인 안 됨입니다` 같은 문장이 산문·목록에 12개 있었고 전부 고쳐졌다.
    def codes(doc: str) -> set[str]:
        return {f["code"] for f in S.scan(doc)["findings"]}

    for name, doc in [
        ("산문 속 `확인 안 됨입니다`", "운영 서버의 시간대 설정은 확인 안 됨입니다.\n"),
        ("연결형 `확인 안 됨이고`", "예비 서버도 받는지는 보내 보지 않아 확인 안 됨이고, 받더라도 순서가 다릅니다.\n"),
        ("볼드로 강조한 꼬리표", "실제 설정값을 보지 못해 이 부분은 **확인 안 됨**으로 둡니다.\n"),
        ("목록 줄 속 문장", "본문 문단입니다.\n\n- 받는 프로그램이 이를 어떻게 다루는지는 확인 안 됨입니다.\n"),
        ("다른 꼬리표(`없음이고`)", "새 속성 하나에 재배포 없음이고 컬럼을 늘리지 않습니다.\n"),
    ]:
        check(f"잡는다: {name}", "K1" in codes(doc), str(codes(doc)))
    for name, doc in [
        ("표 칸의 꼬리표", "| 항목 | 결과 |\n| --- | --- |\n| DNS 설정 | 확인 안 됨 |\n"),
        ("코드 표기로 감싼 이름", "아래는 판단할 수 없어 `확인 안 됨`으로 남긴 항목입니다.\n"),
        ("따옴표로 감싼 이름", '이 칸의 값은 "해당 없음"이고 비워 두지 않습니다.\n'),
        ("인용 블록", "> 운영 서버의 시간대 설정은 확인 안 됨입니다.\n"),
        ("`-음` 으로 끝나는 보통 명사", "어떻게 쓸지는 런타임 마음입니다. 다음 걸음입니다. 남은 물음입니다.\n"),
        ("고친 문장", "운영 서버의 시간대 설정은 확인하지 못했습니다.\n"),
    ]:
        check(f"안 잡는다: {name}", "K1" not in codes(doc), str(codes(doc)))
    r = S.scan("운영 서버의 시간대 설정은 확인 안 됨입니다.\n")
    check("K1 은 S1 이라 한 번으로 등급이 A 아래로 내려간다", r["grade"] not in ("A", "B"), r["grade"])
    check("voice 가 K1 을 면제하면 등급에서 빠진다",
          S.scan("운영 서버의 시간대 설정은 확인 안 됨입니다.\n", {"K1"})["grade"] == "A")

    print("\n[7] K2 — 합쇼체 글에 섞인 해요체 (S3, 등급에 넣지 않는다)")
    hap = "".join(f"{i}번 값을 셉니다. " for i in range(1, 19))
    mixed = hap + "그 값은 맞아요. 이 경로는 달라요.\n"
    r = S.scan(mixed)
    k2 = [f for f in r["findings"] if f["code"] == "K2"]
    check("합쇼체 18문장에 해요체 2문장이 섞이면 K2", bool(k2), str([f["code"] for f in r["findings"]]))
    r_off = S.scan(mixed, {"K2"})
    check("K2 는 S3 이라 등급을 바꾸지 않는다",
          bool(k2) and k2[0]["severity"] == "S3"
          and (r["grade"], r["s1"], r["s2"]) == (r_off["grade"], r_off["s1"], r_off["s2"]),
          f"{r['grade']} vs 면제 시 {r_off['grade']}")
    check("K2 예문은 종결이 보이게 문장 끝을 보인다",
          bool(k2) and any(w.endswith("맞아요.") or w.endswith("달라요.") for w in k2[0]["where"]),
          str(k2[0]["where"] if k2 else ""))
    for name, doc in [
        ("`~세요`·`~죠`·의문 `~까요?` 는 섞임이 아니다",
         hap + "직접 확인해 보세요. 그래서 빠르죠. 왜 그럴까요?\n"),
        ("해요체 한 문장은 우연으로 본다", hap + "그 값은 맞아요.\n"),
        ("고르게 섞은 글(적은 쪽 20% 이상)은 voice 의 선택이다",
         "".join(f"{i}번 값을 셉니다. {i}번 칸을 봐요. " for i in range(1, 10)) + "\n"),
        ("끝에 붙은 괄호 부연은 종결이 아니다",
         hap + "문제가 생기지 않습니다(글자에 점이 없음). 다음으로 넘어갑니다(아래 절 참고).\n"),
    ]:
        check(f"안 잡는다: {name}", "K2" not in codes(doc), str(codes(doc)))
    check("해요체 글에 섞인 합쇼체도 K2",
          "K2" in codes("".join(f"{i}번 값을 봐요. " for i in range(1, 19))
                        + "그 값은 맞습니다. 이 경로는 다릅니다.\n"))

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
