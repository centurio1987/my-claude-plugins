#!/usr/bin/env python3
"""가중치 어휘 스캐너 — 문체 설정의 **정량** 갈래를 잰다.

`scan_ai_style.py` 가 L0 기계 리듬 등급을 낸다면, 이 스캐너는 활성 voice 가 전역 설정을 계승해
정한 **어휘 목록의 가중치**를 본문이 지켰는지 센다.

    가중치  -3 금지 · -2 강한 절제 · -1 절제 · 0 보통 · +1 선호 · +2 적극 · +3 표지

- 음수 항목은 허용량(산문 1,000자당)을 넘으면 적발한다. 금지(-3)는 1회부터.
- +2 이상인데 한 번도 안 쓰면 알린다(+3 은 경고). **억지로 끼워 넣으라는 뜻이 아니다** —
  자리가 왔는데 다른 말을 골랐는지 사람이 본다.
- 분류가 선언한 점검(한 문장 안 겹침 · 분류 밀도)도 함께 본다.
- L0 스캐너가 이미 세는 항목(W·H·D 코드)은 **세지 않는다.** 한 항목을 두 번 판정하지 않는다.

    python3 scan_lexicon.py <파일> [--voice <id>] [--json] [--all]

--voice 가 없으면 전역 설정까지만 적용한다. 종료 코드: 적발 없음 0 · 있음 1.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scan_ai_style as SCAN  # noqa: E402
import style_registry as SR  # noqa: E402


def run(raw: str, voice_id: str | None = None, *, eff: dict | None = None) -> dict:
    eff = eff or SR.effective(voice_id)
    units, sents = SCAN.prose_units(raw)
    r = SR.scan_lexicon(units, sents, eff)
    r["voice"] = voice_id
    return r


def render(path: str, r: dict, show_all: bool = False) -> str:
    out = [f"# 가중치 어휘 스캔: {path}", ""]
    out.append(f"voice `{r['voice'] or '(전역만)'}` · 산문 {r['prose_chars']}자 / {r['sentences']}문장 · "
               f"{'통과' if r['pass'] else '적발 있음'}")
    out.append("")
    if r["over"]:
        out.append("## 허용량 초과 — 음수 가중치")
        for x in sorted(r["over"], key=lambda z: z["weight"]):
            band = SR.WEIGHT_BANDS[x["weight"]]["name"]
            alt = f" → {' / '.join(x['alternatives'][:2])}" if x.get("alternatives") else ""
            out.append(f"- [{band} {x['weight']:+d}] **{x['forms']}** ({x['category_path']}) "
                       f"{x['count']}회 / 허용 {x['allowed']}회{alt}")
            for w in x["where"][:2]:
                out.append(f"    - {w}")
        out.append("")
    if r["category"]:
        out.append("## 분류 점검")
        for c in r["category"]:
            if c["kind"] == "stack":
                out.append(f"- **{c['label']}** 한 문장에 {c['threshold']}개 이상 겹침 — {c['count']}문장")
                for w in c["where"][:2]:
                    out.append(f"    - {w}")
            else:
                out.append(f"- **{c['label']}** 밀도 {c['density']}/1,000자 (기준 {c['threshold']}) — 총 {c['count']}회")
        out.append("")
    if r["unused"]:
        out.append("## 선호 어휘 미사용")
        for x in r["unused"]:
            tag = "경고" if x["weight"] >= 3 else "알림"
            out.append(f"- [{tag} {x['weight']:+d}] **{x['forms']}** ({x['category_path']}) — "
                       f"자리가 왔는데 다른 말을 골랐는지 본다. 억지로 끼워 넣지 않는다")
        out.append("")
    if show_all:
        used = [x for x in r["rows"] if x["verdict"] == "counted" and x["count"]]
        if used:
            out.append("## 사용 횟수")
            for x in sorted(used, key=lambda z: -z["count"]):
                out.append(f"- {x['forms']} ({x['category_path']}, {x['weight']:+d}) {x['count']}회")
            out.append("")
    if not (r["over"] or r["category"] or r["unused"]):
        out.append("적발 없음.")
    return "\n".join(out).rstrip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--voice")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true", help="사용 횟수 전체도 보인다")
    args = ap.parse_args()
    raw = Path(args.path).read_text(encoding="utf-8")
    if args.voice and not SR.voice_exists(args.voice):
        print(f"voice '{args.voice}' 가 레지스트리에 없다 ({SR.registry_home()})", file=sys.stderr)
        return 2
    problems = SR.validate_all_for(args.voice)
    if problems:
        # 잘못된 설정으로 잰 결과는 믿을 수 없다. 조용히 재지 않고 멈춘다.
        print("문체 설정이 검증에 실패해 재지 않는다 — `authoring.py style validate` 로 고친다:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 2
    r = run(raw, args.voice)
    print(json.dumps(r, ensure_ascii=False, indent=2) if args.json else render(args.path, r, args.all))
    return 0 if r["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
