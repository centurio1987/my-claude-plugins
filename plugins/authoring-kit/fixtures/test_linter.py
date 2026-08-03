#!/usr/bin/env python3
"""플레이스홀더 린터 — 세는 단위 검증.

`[...]` 는 슬롯 표기이기도 하지만 **배열 리터럴·인덱스이기도 하다.** 알고리즘 글에서는
후자가 압도적이라, 안 걸러 내면 정상 본문 수십 건이 미해결 슬롯으로 잡혀 발행이 막힌다.
실제로 신규 가이드 1건이 그렇게 막혔다(61건 전부 오탐).

여기 모인 케이스는 오탐과 **진짜로 잡아야 하는 것**을 함께 둔다. 한쪽만 통과하면 실패다.

실행:  python3 fixtures/test_linter.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("lintp", PLUGIN / "scripts" / "lint_placeholders.py")
L = importlib.util.module_from_spec(spec)
sys.modules["lintp"] = L
spec.loader.exec_module(L)

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
    print("플레이스홀더 린터 — 세는 단위\n")

    print("[1] 배열 리터럴·인덱스는 슬롯이 아니다")
    for s in ("3, 2, 2, 4, 2", "1,2,3,4", "i", "K", "3", "0", "1, N+1, 1, N+1, …", "0, 0, 1, 2, 0"):
        check(f"`[{s}]` 는 슬롯이 아니다", not L._looks_like_slot(s))

    print("\n[2] 진짜 슬롯은 잡아야 한다")
    for s in ("이름", "한 줄 요약", "s0001", "글 제목 — 무엇을 끝까지 이해시킬 것인가",
              "YYYY-MM-DD", "회사명"):
        check(f"`[{s}]` 는 슬롯이다", L._looks_like_slot(s))

    print("\n[3] 알고리즘 본문이 통째로 오탐되지 않는다")
    prose = (
        "`N = 5`, `A = [3, 4, 4, 6, 1, 4, 4]` 를 넣으면 결과는 `[3, 2, 2, 4, 2]` 예요.\n"
        "`counters[i]` 를 올리고 `A[K]` 를 확인합니다. 중간 상태는 `[0, 0, 1, 2, 0]` 입니다.\n"
    )
    r = L.scan(prose, is_mdx=False)
    check("배열이 든 산문에서 레거시 적발 0",
          not r["legacy"].get("bracket-inline"), str(r["legacy"]))

    print("\n[4] 그래도 std-v1 미해결 슬롯은 잡는다")
    draft = "제목은 {{ header.title }} 이고 본문은 {{ about.body:cto }} 입니다.\n"
    r2 = L.scan(draft, is_mdx=False)
    check("`{{ id }}` 슬롯 2개를 잡는다", len(r2["slots"]) == 2, str(r2["slots"]))

    mdx = "여기 {/* @slot:header.title */} 자리가 있습니다.\n"
    r3 = L.scan(mdx, is_mdx=True)
    check("mdx 는 `{/* @slot:id */}` 표기를 잡는다", r3["slots"] == ["header.title"], str(r3["slots"]))

    print("\n[5] 집필 지시·마커·조건블록")
    doc = ("<!-- @write: 여기에 도입을 쓴다 -->\n본문 @[추정] 입니다.\n"
           "<!-- @if: pos=cto -->조건부<!-- @end -->\n")
    r4 = L.scan(doc, is_mdx=False)
    check("집필 지시를 잡는다", r4["writes"] == 1, str(r4["writes"]))
    check("집필 마커를 잡는다", r4["markers"] == ["추정"], str(r4["markers"]))
    check("조건블록 짝이 맞는다", r4["if_open"] == r4["if_close"] == 1)

    unbalanced = "<!-- @if: pos=cto -->조건부\n"
    r5 = L.scan(unbalanced, is_mdx=False)
    check("짝이 안 맞으면 드러난다", r5["if_open"] != r5["if_close"])

    print("\n[6] 못 읽은 파일을 깨끗하다고 하지 않는다")
    check("UnreadableFile 예외가 정의돼 있다", hasattr(L, "UnreadableFile"))

    print("\n[7] set 단계 — 미룬 슬롯과 그냥 남은 슬롯을 가른다")
    # resume 는 draft → set → format 3단계다. `03_set` 은 직무 분기 슬롯을 **일부러** 남기고
    # 4차 형식화가 직무별로 해소한다. 그걸 final 로 재면 렌더 계약이 실패로 잡힌다 — 실제로 그랬다.
    dfr, stray = L.deferred_slots(["pos:title", "header.name"], ["pos-block"])
    check("legacy_accept 로 선언한 슬롯은 미룬 것으로 센다", dfr == ["pos:title"], f"{dfr}")
    check("선언 안 한 슬롯은 그냥 남은 것이다", stray == ["header.name"], f"{stray}")
    dfr2, stray2 = L.deferred_slots(["pos:title"], [])
    check("legacy_accept 가 비면 아무것도 미룰 수 없다",
          dfr2 == [] and stray2 == ["pos:title"], f"미룸 {dfr2} / 남음 {stray2}")

    print(f"\n{'='*56}")
    print(f"통과 {PASSES} · 실패 {len(FAILS)}")
    if FAILS:
        print("\n실패 목록:")
        for f in FAILS:
            print(f"  - {f}")
        return 1
    print("린터 통과.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
