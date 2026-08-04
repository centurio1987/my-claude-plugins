#!/usr/bin/env python3
"""Rule traceability matrix — 이관 중 규칙이 조용히 사라지는 것을 막는다.

왜 필요한가: 집필 규칙이 세 프로젝트에 흩어져 있고, 이제 L0(공통 원칙)/L1(퍼소나 voice)/
L2(글 명세) 세 층으로 재배치된다. 재배치는 사람이 판단해야 하는 일이지만, **하나도 빠뜨리지
않았다는 것**은 기계가 증명해야 한다. 이 스크립트가 그 증명을 담당한다.

두 커맨드가 있고 역할이 다르다:

  suggest  현행 문서에서 규칙 항목 **후보**를 뽑아 TSV로 낸다. 보조 도구다 —
           문서마다 형식이 달라(헤딩/표/번호목록/체크리스트가 섞임) 자동 추출만으로는
           신뢰할 수 없다. 사람이 검토해 axis 와 layer_dest 를 채워 확정한다.

  verify   확정된 인벤토리를 새 L0/L1/L2 배치와 대조한다. 이쪽이 본체다.
           유실·미분류·UNTAGGED 가 하나라도 있으면 비-0 으로 죽는다.

갈래(axis) 태그 규약: 규칙 항목 헤딩 줄 끝에 `<!-- axis: grammar -->` 를 단다.
소유 층이 아닌 축이 문서에 있으면 갈래 위반이다(authoring.py validate 소관).

사용법:
    python3 trace_rules.py suggest <파일|디렉토리> ... [--out RULES_INVENTORY.tsv]
    python3 trace_rules.py verify  --inventory RULES_INVENTORY.tsv --root <새 배치 루트> ...
    python3 trace_rules.py codes   <파일> ...          # 코드 목록만 (드리프트 대조용)
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

# ── 규칙 항목으로 볼 패턴 ────────────────────────────────────────────────
# 문서마다 형식이 다르다. 넓게 잡고 사람이 걸러내는 편이, 좁게 잡아 놓치는 것보다 낫다.
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # ### A1. 영어 비유·수사의 직역        /  ### R3 볼드 절제  /  ### F2. 문장 호흡
    ("heading", re.compile(r"^#{2,4}\s+(?P<code>[A-Z]{1,4}\d{1,2})[.)]?\s+(?P<title>.+?)\s*$")),
    # ### §D. 표현이 어색한 자리
    ("section", re.compile(r"^#{2,4}\s+§?(?P<code>[A-Z])[.)]\s+(?P<title>.+?)\s*$")),
    # | **P5** | 볼드 남용 | ...        /  | A10 | 인수(引受) | ...
    ("table", re.compile(r"^\|\s*\*{0,2}(?P<code>[A-Z]{1,4}\d{1,2})\*{0,2}\s*\|\s*(?P<title>[^|]+)")),
    # - **[MUST] A1 점진적 공개** — …      (품질 체크리스트의 지배적 형식. 세 프로젝트 루브릭이 모두 이 꼴이다)
    ("checklist", re.compile(
        r"^\s*[-*]\s+\*\*\[(?P<level>MUST|SHOULD|IF-APPLICABLE)\]\s+(?P<code>[A-Z]{1,3}\d{1,2})\s+(?P<title>.+?)\*\*")),
    # 1. **존댓말 설명체.** "~예요 / ~합니다"…      (문체 규칙 10 형식)
    ("numbered", re.compile(r"^\s{0,3}(?P<code>\d{1,2})\.\s+\*\*(?P<title>[^*]+)\*\*")),
]

AXIS_TAG = re.compile(r"<!--\s*axis:\s*(?P<axis>[a-z-]+)\s*-->")
FENCE = re.compile(r"^\s*```")

VALID_AXES = {
    "evidence", "grammar", "machine-rhythm",
    "register", "rhythm", "device", "lexicon",
    "structure", "scope-principle",
}
VALID_LAYERS = {"L0", "L1", "L2", "DROP"}

COLUMNS = ["source_file", "rule_id", "text_hash", "axis", "layer_dest", "dest_ref", "status", "title"]

# `dest_ref` 가 있는 이유: 이관은 **복사가 아니라 재작성**이다. 특정 저자를 가리키던 문구를
# voice-중립으로 고치고, 여러 규칙을 하나로 합치고, 이름을 바꾼다. 그러면 텍스트 해시가 달라지고
# 해시 대조만 하는 verify 는 멀쩡히 옮긴 규칙을 전부 "유실"이라고 부른다.
# 그래서 재작성된 규칙은 **목적지를 명시**한다 — `L0_PRINCIPLES.md#C6` 처럼.
# verify 는 그 파일에 그 코드가 실제로 있는지만 본다. 해시는 손대지 않은 규칙에만 쓴다.


def norm(text: str) -> str:
    """비교용 정규화 — 공백·강조·따옴표 차이로 유실 오탐이 나지 않게."""
    t = re.sub(r"[*_`]", "", text)
    t = re.sub(r"[\s ]+", " ", t)
    t = t.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    return t.strip().lower()


def text_hash(text: str) -> str:
    return hashlib.sha1(norm(text).encode("utf-8")).hexdigest()[:10]


def iter_md(targets: list[str]):
    for t in targets:
        p = Path(t).expanduser()
        if p.is_dir():
            yield from sorted(q for q in p.rglob("*.md") if "_deprecated" not in q.parts)
        elif p.is_file():
            yield p


HEADING = re.compile(r"^(?P<hashes>#{1,6})\s+")


def extract(path: Path) -> list[dict]:
    """한 파일에서 규칙 항목 후보를 뽑는다. 코드펜스 안은 건너뛴다(예시 코드가 규칙이 아니다).

    axis 는 **섹션 단위로 상속된다.** 표 안의 항목(`| D1 | … |`)마다 HTML 주석을 끼워 넣으면
    표가 깨지므로, 상위 헤딩에 `<!-- axis: grammar -->` 를 한 번 달면 그 아래 항목들이 물려받는다.
    항목이 자기 태그를 직접 달면 그쪽이 이긴다(더 구체적인 선언이 우선).
    """
    out: list[dict] = []
    seen: set[str] = set()
    in_fence = False
    axis_by_depth: dict[int, str] = {}

    def current_axis() -> str:
        return axis_by_depth[max(axis_by_depth)] if axis_by_depth else ""

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence or not raw.strip():
            continue

        # 헤딩이면 섹션 axis 문맥을 갱신한다 — 항목 추출보다 먼저.
        h = HEADING.match(raw)
        if h:
            depth = len(h.group("hashes"))
            for d in [d for d in axis_by_depth if d > depth]:
                del axis_by_depth[d]          # 더 깊은 섹션의 선언은 여기서 만료
            tag = AXIS_TAG.search(raw)
            if tag:
                axis_by_depth[depth] = tag.group("axis")
            elif depth in axis_by_depth:
                del axis_by_depth[depth]      # 같은 깊이의 무태그 헤딩은 이전 선언을 닫는다

        for kind, pat in PATTERNS:
            m = pat.match(raw)
            if not m:
                continue
            code = m.group("code")
            # axis 태그는 메타데이터지 제목이 아니다. 해시에 섞이면 "태그를 달았다"는 이유만으로
            # 같은 규칙이 유실로 잡힌다 — 반드시 떼고 비교한다.
            title = AXIS_TAG.sub("", m.group("title")).strip().rstrip("|").strip()
            # 번호 목록은 코드가 1..N 이라 파일 안에서만 유일하다 — N 접두사로 네임스페이스.
            rule_id = f"{code}" if kind != "numbered" else f"N{code}"
            key = f"{rule_id}|{norm(title)[:40]}"
            if key in seen:
                continue
            seen.add(key)
            own = AXIS_TAG.search(raw)
            axis = own.group("axis") if own else current_axis()
            # 무엇이 "갈래 태그를 반드시 달아야 하는 규칙"인가.
            #   · 코드가 붙은 항목(A1·D5·P3…)은 언제나 규칙이다 — 태그가 없으면 UNTAGGED.
            #   · 코드 없는 번호 항목(`1. **…**`)은 규칙 카탈로그·체크리스트 안에 있을 때만 규칙이다.
            #     서론의 설명용 나열까지 규칙으로 세면 UNTAGGED 오탐이 쏟아진다.
            #   suggest 단계(태그 없는 현행 문서)에서는 둘 다 후보로 뽑아 사람이 거른다.
            ruleish = kind != "numbered" or bool(axis)
            out.append({
                "source_file": str(path),
                "rule_id": rule_id,
                "text_hash": text_hash(title),
                "axis": axis,
                "layer_dest": "",
                "status": "candidate",
                "title": title,
                "_line": lineno,
                "_kind": kind,
                "_ruleish": ruleish,
            })
            break
    return out


def read_tsv(p: Path) -> list[dict]:
    rows = []
    lines = p.read_text(encoding="utf-8").splitlines()
    if not lines:
        return rows
    header = lines[0].split("\t")
    for ln in lines[1:]:
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        vals = ln.split("\t")
        vals += [""] * (len(header) - len(vals))
        rows.append(dict(zip(header, vals)))
    return rows


def write_tsv(rows: list[dict], out: Path) -> None:
    body = ["\t".join(COLUMNS)]
    for r in rows:
        body.append("\t".join((r.get(c, "") or "").replace("\t", " ") for c in COLUMNS))
    out.write_text("\n".join(body) + "\n", encoding="utf-8")


def cmd_suggest(args) -> int:
    rows: list[dict] = []
    per_file: dict[str, int] = {}
    for f in iter_md(args.targets):
        got = extract(f)
        if got:
            per_file[str(f)] = len(got)
            rows.extend(got)
    out = Path(args.out).expanduser()
    write_tsv(rows, out)
    print(f"# 후보 {len(rows)}건 → {out}")
    for f, n in sorted(per_file.items(), key=lambda kv: -kv[1]):
        print(f"  {n:4d}  {f}")
    print("\n# 다음: axis 와 layer_dest 를 사람이 채워 status 를 confirmed 로 바꾼다.")
    print(f"#   axis:       {' | '.join(sorted(VALID_AXES))}")
    print(f"#   layer_dest: {' | '.join(sorted(VALID_LAYERS))}  (DROP 은 사유를 status 에 적는다)")
    return 0


def cmd_codes(args) -> int:
    """파일별 규칙 코드 집합 — 같은 문서의 판본 간 드리프트를 눈으로 대조할 때."""
    table: dict[str, set[str]] = {}
    for f in iter_md(args.targets):
        table[str(f)] = {r["rule_id"] for r in extract(f)}
    names = list(table)
    everything = sorted(set().union(*table.values()) if table else set(),
                        key=lambda c: (c[0], int(re.sub(r"\D", "", c) or 0)))
    width = max((len(Path(n).parent.name + "/" + Path(n).name) for n in names), default=10)
    print("code".ljust(8) + "".join(f"  {Path(n).parent.name}/{Path(n).name}"[:width + 2].ljust(width + 2) for n in names))
    for c in everything:
        row = c.ljust(8)
        for n in names:
            row += ("  O" if c in table[n] else "  ·").ljust(width + 2)
        print(row)
    print()
    for n in names:
        print(f"  {len(table[n]):3d}  {n}")
    return 0


def cmd_verify(args) -> int:
    inv = Path(args.inventory).expanduser()
    if not inv.exists():
        print(f"인벤토리가 없다: {inv}", file=sys.stderr)
        return 2
    rows = read_tsv(inv)
    if not rows:
        print(f"인벤토리가 비어 있다: {inv}", file=sys.stderr)
        return 2

    # 새 배치에서 실제로 존재하는 항목 수집
    present: dict[str, list[dict]] = {}          # text_hash → 항목
    by_file: dict[str, set[str]] = {}            # 파일명 → 그 파일의 rule_id 집합
    untagged: list[dict] = []
    for f in iter_md(args.roots):
        got = extract(f)
        by_file[f.name] = {r["rule_id"] for r in got}
        for r in got:
            present.setdefault(r["text_hash"], []).append(r)
            if r.get("_ruleish") and not r["axis"]:
                untagged.append(r)

    expect = set(args.expect.split(",")) if args.expect else {"L0", "L1", "L2"}
    missing, unclassified, dropped, pending, ok = [], [], [], [], 0
    for r in rows:
        dest = (r.get("layer_dest") or "").strip()
        if not dest:
            unclassified.append(r); continue
        if dest == "DROP":
            dropped.append(r); continue
        if dest not in VALID_LAYERS:
            unclassified.append(r); continue
        if dest not in expect:
            pending.append(r); continue      # 아직 만들 차례가 아닌 층

        ref = (r.get("dest_ref") or "").strip()
        if ref:
            # 목적지 명시가 있으면 **그 파일에 그 코드가 있는지**만 본다(재작성 허용).
            fname, _, code = ref.partition("#")
            if code and code in by_file.get(fname, set()):
                ok += 1
            elif not code and fname in by_file:
                ok += 1
            else:
                missing.append(r)
        elif r["text_hash"] in present:
            ok += 1
        else:
            missing.append(r)

    print(f"인벤토리 {len(rows)}건 · 검증 대상 층 {sorted(expect)} · 확인 {ok}건")
    if pending:
        print(f"대기 {len(pending)}건 (검증 대상 층이 아님 — 이후 Phase 에서 이관)")
    fail = False
    if unclassified:
        fail = True
        print(f"\n[미분류] layer_dest 가 비었거나 잘못됨 — {len(unclassified)}건")
        for r in unclassified[:20]:
            print(f"  {r['rule_id']:6s} {r.get('title','')[:60]}  ({Path(r['source_file']).name})")
    if missing:
        fail = True
        print(f"\n[유실] 새 배치에서 찾지 못함 — {len(missing)}건")
        for r in missing[:30]:
            print(f"  {r['rule_id']:6s} → {r['layer_dest']:4s}  {r.get('title','')[:55]}")
    if untagged:
        fail = True
        print(f"\n[UNTAGGED] 새 배치에 axis 태그 없는 규칙 — {len(untagged)}건")
        for r in untagged[:20]:
            print(f"  {r['rule_id']:6s} {r.get('title','')[:55]}  ({Path(r['source_file']).name}:{r['_line']})")
    if dropped:
        # DROP 은 실패가 아니다. 다만 조용히 사라지면 안 되므로 반드시 보고한다.
        print(f"\n[DROP] 의도적으로 버린 규칙 — {len(dropped)}건 (사유는 status 열)")
        for r in dropped:
            print(f"  {r['rule_id']:6s} {r.get('title','')[:45]}  ← {r.get('status','(사유 없음)')}")
        no_reason = [r for r in dropped if not r.get("status") or r["status"] == "candidate"]
        if no_reason:
            fail = True
            print(f"  ! 사유가 없는 DROP {len(no_reason)}건 — 조용한 유실은 허용하지 않는다")

    print("\n" + ("실패" if fail else "통과 — 규칙 유실 0"))
    return 1 if fail else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("suggest", help="현행 문서에서 규칙 후보 추출 (사람이 확정)")
    s.add_argument("targets", nargs="+")
    s.add_argument("--out", default="RULES_INVENTORY.tsv")
    s.set_defaults(func=cmd_suggest)

    c = sub.add_parser("codes", help="파일별 규칙 코드 대조표 (판본 드리프트용)")
    c.add_argument("targets", nargs="+")
    c.set_defaults(func=cmd_codes)

    v = sub.add_parser("verify", help="확정 인벤토리 ↔ 새 배치 대조")
    v.add_argument("--inventory", required=True)
    v.add_argument("--root", dest="roots", nargs="+", required=True)
    v.add_argument("--expect", help="지금 검증할 층 (예: L0,L1). 나머지는 '대기'로 뺀다")
    v.set_defaults(func=cmd_verify)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
