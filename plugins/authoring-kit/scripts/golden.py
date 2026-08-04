#!/usr/bin/env python3
"""골든셋 회귀 — 이관 후 파이프라인이 지금 쓰는 글을 재현하는지 잰다.

**재현의 대상은 내용과 구성이지 문장이 아니다.**
자연스러운 한국어 규칙이 지금은 프로젝트마다 다르게 적용돼 있어서, 통일하면 문장이 달라진다.
그건 회귀가 아니라 이 작업의 성과다. 그래서 갈래마다 판정 방식이 다르다:

    내용   재현 대상 — 사실·수치·코드·핵심 주장이 빠지거나 달라지면 실패
    구성   재현 대상 — 항목 골격·순서·필수 충족이 어긋나면 실패
    문체   **동일이 아니라 악화 없음** — 등급이 좋아지면 통과
    voice  새로 생기는 기준 — 활성 퍼소나의 선언과 금지를 지키는가

LLM 산출물은 바이트 동일이 불가능하다. 그래서 "같은가"가 아니라 "무엇이 어떻게 달라졌는가"를
보고하고, **최종 판정은 사람이 한다**(§5.3 사람 승인 게이트).

사용법:
    golden.py measure <파일> --spec <id> --project <dir> [--voice <id>]   # 기준값 1건
    golden.py baseline --set <설정.json> --out GOLDEN_BASELINE.json        # 골든셋 전체
    golden.py compare --baseline <json> --candidate <파일> --id <골든셋 id>
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name: str):
    """옆 스크립트를 모듈로 가져온다.

    `sys.modules` 등록이 필수다 — 빼면 `@dataclass` 가 자기 모듈을 못 찾아
    `AttributeError: 'NoneType' object has no attribute '__dict__'` 로 죽는다.
    """
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


A = _load("authoring")
SCAN = _load("scan_ai_style")

FENCE = re.compile(r"^\s*```")
HEADING = re.compile(r"^(#{1,4})\s+(.+?)\s*$")
# 본문에서 뽑아낼 "사실" 후보 — 이게 달라지면 내용이 달라진 것이다.
# 뒷경계를 숫자·점으로만 막는다. `\w` 로 막으면 **한글 조사가 붙은 수치가 통째로 사라진다** —
# `ISO 14044와`, `TOEIC 915점`, `2024년` 이 전부 미검출이었다. 한국어 글을 재는 도구에서
# 이건 잡음이 아니라 결함이다: 없는 유실을 만들어 내고, 그 잡음에 진짜 유실이 묻힌다.
# 앞경계는 `\w` 를 유지한다 — `AWS3` 의 `3` 같은 식별자 꼬리를 수치로 세지 않기 위해서다.
NUM = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)*(?:[eE][-+]?\d+)?(?![\d.])")
BIGO = re.compile(r"O\(\s*[^)]{1,40}\)")
IDENT = re.compile(r"`([^`\n]{1,60})`")


def sections(text: str) -> list[dict]:
    """헤딩 골격. 코드펜스 안의 `#` 은 헤딩이 아니다."""
    out, in_fence = [], False
    for i, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING.match(line)
        if m:
            out.append({"level": len(m.group(1)), "title": m.group(2), "line": i})
    return out


def norm_complexity(s: str) -> str:
    """복잡도 표기를 정규화해 **표기 차이를 유실로 오판하지 않게** 한다.

    같은 것을 다르게 쓴다:  O(qn) ≡ O(nq) ≡ O(q·n) ≡ O(q \\cdot n)
                            O(n\\sqrt{q}) ≡ O(n√q)
    문자열 그대로 비교하면 이 전부가 '유실'로 잡히고, 진짜 유실(정렬 비용 O(q log q) 누락)이
    잡음에 묻힌다. 1라운드에서 실제로 그랬다.

    곱셈만으로 이뤄진 항은 인자를 정렬해 순서 차이를 없앤다. 덧셈이 섞인 항은
    구조가 의미를 가지므로 정렬하지 않는다.
    """
    t = s
    for a, b in ((r"\cdot", "*"), (r"\log", "log"), (r"\sqrt", "sqrt"),
                 (r"\lfloor", ""), (r"\rfloor", ""), (r"\,", ""), (r"\;", "")):
        t = t.replace(a, b)
    t = t.replace("·", "*").replace("√", "sqrt").replace("×", "*")
    t = re.sub(r"[{}\s]", "", t)
    m = re.match(r"^O\((.*)\)?$", t)
    inner = (m.group(1) if m else t).rstrip(")")
    if "+" not in inner and "log" not in inner:
        # 분모를 떼고 분자만 정규화한 뒤 다시 붙인다.
        num, sep, den = inner.partition("/")
        parts = [p for p in re.split(r"\*", num) if p]
        expanded: list[str] = []
        for p in parts:
            if re.fullmatch(r"[a-zA-Z]{2,}", p) and "sqrt" not in p:
                expanded.extend(list(p))   # qn 처럼 붙어 있으면 문자 단위로
            else:
                expanded.append(p)
        # 반복 인자를 거듭제곱으로 접는다: n*n ≡ n^2
        counts: dict[str, int] = {}
        for p in expanded:
            counts[p] = counts.get(p, 0) + 1
        num = "*".join(f"{k}^{v}" if v > 1 else k for k, v in sorted(counts.items()))
        inner = num + sep + den
    return f"O({inner})"


def facts(text: str) -> dict:
    """내용 항목의 재료. 수치·복잡도·식별자·코드블록을 센다.

    문장은 담지 않는다 — 문장이 달라지는 건 정상이기 때문이다.
    """
    body, in_fence, code_blocks = [], False, []
    buf: list[str] = []
    for line in text.splitlines():
        if FENCE.match(line):
            if in_fence:
                code_blocks.append("\n".join(buf))
                buf = []
            in_fence = not in_fence
            continue
        (buf if in_fence else body).append(line)
    prose = "\n".join(body)
    raw_cx = set(BIGO.findall(prose + "\n".join(code_blocks)))
    return {
        "numbers": sorted(set(NUM.findall(prose))),
        "complexities": sorted(raw_cx),
        # 비교는 정규화한 쪽으로 한다. 원본 표기는 사람이 보라고 남긴다.
        "complexities_norm": sorted({norm_complexity(x) for x in raw_cx}),
        "identifiers": sorted(set(IDENT.findall(prose))),
        "code_blocks": len(code_blocks),
        "code_chars": sum(len(c) for c in code_blocks),
        "prose_chars": len(prose),
    }


# 장치는 이름이 kebab-case 라 본문에서 직접 못 찾는다. 대신 **흔적**을 센다.
# 전부 휴리스틱이다 — 0 이 곧 부재는 아니고, 탐지가 못 잡은 것일 수도 있다.
# 그래서 판정은 "기준값에 뚜렷하게 있던 장치가 사라졌는가"만 보고, 최종 확인은 사람이 한다.
#
# **표에 없는 장치는 통과가 아니라 `manual_check_devices` 로 나간다.** 여기 키를
# 늘리는 것이 voice 를 추가할 때의 일이고, 못 늘리겠으면 그냥 두면 된다 — 사람이 본다.
DEVICE_PATTERNS: dict[str, str] = {
    # ── ppangtolab-teacher ──
    "ascii-art-after-concept": r"```text",
    # 상태 변화를 전/후로 나란히 보였는가. 영문 Before/After 와 한국어 '분할 전/후' 류를 함께.
    "before-after-diagram": r"[Bb]efore\b|[Aa]fter\b|(?:변형|분할|회전|삽입|삭제|이동|병합)\s*(?:전|후)\b",
    "misconception-callout": r"헷갈리기 쉬운|오해|착각",
    "key-line-pointing": r"가장 (?:중요한|실수가 잦은)\s*(?:줄|부분|것)|이 (?:두 )?줄이",
    "mnemonic-quote": r"^>\s",
    # 독자에게 손을 움직이게 하는 청유·확인. `확인` 뒤에서만 찾으면 '관찰해 봅시다'를 놓친다.
    "midway-check-question": r"봅시다|볼까요|해 보세요|해 보자|확인해\s*(?:보|주)",
    "self-check-closing": r"스스로 점검하기",
    # ── yundeok ──
    # 고전 앵커 — 한자 원문 인용이 표식이다. 한글 음차(`격물`)는 세지 않는다.
    "classical-anchor": r"[一-鿿]{2,}|論語|孫子|大學|中庸",
    "honest-limitation": r"한계|제약이|미흡|부족했|아쉬(?:운|웠)|못 (?:했|한) 것",
    "tradeoff-framing": r"트레이드오프|trade-?off|맞바꾸|대신 (?:잃|포기)|희생하|얻는 대신",
    # 1인칭 고백 — 인칭 대명사 단독은 흔해서 못 쓴다. **자기 오류 서술과 붙어 있을 때**만 센다.
    "first-person-confession-arc": r"(?:저는|제가|나는|내가)[^\n]{0,40}(?:몰랐|틀렸|실패|착각|놓쳤|부끄|오판)",
}


VISUAL = re.compile(r"^\s*(```|!\[|<[A-Z][A-Za-z]*\s|\|)")
FENCE_LINE = re.compile(r"^\s*(```|~~~)")


def longest_prose_run(text: str) -> int:
    """시각 자료 없이 이어지는 산문 문단의 **최장 연속 길이**.

    총량만 세면 그림 30개가 앞쪽에 몰려도 통과한다. 선생님 voice 는
    "산문 3~4문단이 그림 없이 이어지면 신호 위반"이라고 **분포**를 규정하는데,
    장치 흔적 카운트로는 그걸 잴 수 없다. 그래서 따로 잰다.

    코드펜스·이미지·JSX 컴포넌트·표를 시각 자료로 본다. 헤딩은 구간을 끊는다 —
    절이 바뀌면 호흡도 새로 시작하기 때문이다.
    """
    # **코드펜스를 먼저 통째로 접는다.** 빈 줄로 블록을 쪼개면 펜스 안의 여백이 블록
    # 경계가 되어, 그림 뒷부분이 평범한 산문 문단으로 잡힌다. 그림 안의 여백을 산문으로
    # 세는 것은 오탐이고, 실제로 그것 때문에 한 편이 위반 7 로 잡혔다(진짜 값은 4 였다).
    folded, in_fence, buf = [], False, []
    for line in text.splitlines():
        if FENCE_LINE.match(line):
            if in_fence:
                folded.append("```")            # 펜스 한 덩어리를 한 줄로 접는다
            in_fence = not in_fence
            if in_fence:
                continue
            continue
        if in_fence:
            continue
        folded.append(line)
    text = "\n".join(folded)
    run = best = 0
    for block in re.split(r"\n\s*\n", text):
        b = block.strip()
        if not b:
            continue
        if b.startswith("#"):
            run = 0
            continue
        if VISUAL.match(b):
            run = 0
            continue
        # 목록·인용은 **산문이 아니다.** 규칙이 말하는 것은 "산문 N문단"이므로
        # 세지 않는다. 그렇다고 시각 자료도 아니라서 구간을 끊지도 않는다.
        lines = [x.strip() for x in b.splitlines() if x.strip()]
        if all(re.match(r"^([-*+]|\d+\.)\s", x) for x in lines) or all(x.startswith(">") for x in lines):
            continue
        run += 1
        best = max(best, run)
    return best


def voice_compliance(text: str, voice_id: str) -> dict:
    """활성 voice 의 금지 목록이 본문에 나타나는지, 선언한 장치가 실제로 쓰였는지."""
    try:
        v, _ = A.load_voice(voice_id)
    except FileNotFoundError:
        return {"voice": voice_id, "error": "voice 를 찾을 수 없다"}
    devices = v.get("axes", {}).get("device", [])
    traces = {k: len(re.findall(p, text, re.M)) for k, p in DEVICE_PATTERNS.items()}
    declared_traces = {k: n for k, n in traces.items() if k in devices}
    # 탐지기가 없는 장치는 **조용히 빠지게 두지 않는다.** 한 voice 의 장치명만
    # 하드코딩돼 있던 탓에 다른 voice 는 device_traces 가 늘 `{}` 였고, voice 항목이
    # 공허하게 통과했다. 거짓 실패보다 거짓 통과가 나쁘다.
    manual = [d for d in devices if d not in DEVICE_PATTERNS]
    return {
        "voice": voice_id,
        "declared_devices": devices,
        "device_traces": declared_traces,
        # 기계로 못 재는 장치 — 통과로 세지 않고 사람에게 넘긴다.
        "manual_check_devices": manual,
        # 분포 — 총량이 아니라 **어디에 있는가**. 3 이상이면 voice 가 말한 신호 위반 구간이다.
        "max_prose_run_without_visual": longest_prose_run(text),
        "register_hint": {
            "존댓말_종결": len(re.findall(r"(입니다|합니다|예요|봅시다)\.", text)),
            "평서체_종결": len(re.findall(r"(이다|한다|였다)\.", text)),
        },
    }


FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)


def strip_draft_scaffolding(text: str, spec: dict | None) -> str:
    """내용 대조에서 **초안 뼈대**를 뺀다.

    프론트매터와 draft 전용 절(보완 리포트 등)은 글의 내용이 아니라 집필 기록이다.
    거기 적힌 wiki 링크·ORD 번호·갭 ID 를 내용으로 세면, 재생성본은 그 기록을
    물려받지 않았다는 이유만으로 매번 "유실"을 뒤집어쓴다. 실제로 이력서 기준값에서
    유실로 잡힌 19건 중 사실은 **0건**이었고 전부 이 뼈대에서 나왔다.

    무엇이 draft 전용인지는 도구가 정하지 않는다 — **명세가 정한다.**
    """
    text = FRONTMATTER.sub("", text)
    if not spec:
        return text
    drop = [s for s in spec.get("sections", [])
            if s.get("heading_fixed") and "draft" in (s.get("condition") or "")]
    for s in drop:
        head = s["heading"]
        # 그 절부터 다음 동급 헤딩 전까지를 잘라 낸다. 마지막 절이면 끝까지.
        level = len(head) - len(head.lstrip("#"))
        text = re.sub(rf"^{re.escape(head)}\s*$.*?(?=^#{{1,{level}}} |\Z)",
                      "", text, flags=re.S | re.M)
    return text


def measure(path: Path, spec_id: str | None, project: Path, voice_id: str | None) -> dict:
    text = path.read_text(encoding="utf-8")
    waived = SCAN.load_voice_context(voice_id) if voice_id else set()
    style = SCAN.scan(text, waived)
    secs = sections(text)
    spec: dict | None = None
    if spec_id:
        try:
            spec, _ = A.load_spec(spec_id, project)
        except FileNotFoundError:
            spec = None
    # 내용 항목만 뼈대를 벗긴 본문을 쓴다. 구성·문체는 글 전체를 그대로 본다.
    body = strip_draft_scaffolding(text, spec)
    out: dict = {
        "file": str(path),
        "lines": len(text.splitlines()),
        "spec": spec_id,
        "voice": voice_id,
        "structure": {
            "h2": [s["title"] for s in secs if s["level"] == 2],
            "h3": [s["title"] for s in secs if s["level"] == 3],
        },
        "content": facts(body),
        "style": {"grade": style["grade"], "s1": style["s1"], "s2": style["s2"],
                  "s3": style["s3"], "waived": style.get("waived", []),
                  "codes": sorted({f["code"] for f in style["findings"]})},
    }
    if voice_id:
        out["voice_compliance"] = voice_compliance(text, voice_id)
    if spec_id and spec is None:
        out["spec_conformance"] = {"error": f"spec {spec_id} 없음"}
    elif spec:
        want = [x for x in sorted(spec.get("sections", []), key=lambda z: z.get("order", 0))
                if x.get("required") and not x.get("parent")]
        have = out["structure"]["h2"]
        missing = [x["label"] for x in want
                   if x.get("heading_fixed") and x["heading"].lstrip("#").strip() not in have]
        out["spec_conformance"] = {
            "required_h2": len(want), "present_h2": len(have), "missing": missing,
        }
        # 구성 대조가 어느 제목을 문자 그대로 요구하는지 — compare() 가 이걸 읽는다.
        out["fixed_headings"] = [x["heading"].lstrip("#").strip()
                                 for x in spec.get("sections", [])
                                 if x.get("heading_fixed") and x.get("heading")]
    return out


def compare(base: dict, cand: dict) -> dict:
    """갈래마다 다른 잣대로 잰다. 문체는 '악화 없음'만 본다."""
    GRADE = {"A": 4, "B": 3, "C": 2, "D": 1}
    r: dict = {"id": base.get("id"), "verdict": {}, "detail": {}}

    # 구성 — **명세 대조**다. 문자열 동일이 아니라 "섹션이 있고 순서가 같은가"를 본다.
    #
    # 문자열 동일을 요구하면 `heading_fixed: false` 인 절에서 반드시 깨진다.
    # 명세가 제목을 저자에게 맡겨 놓고 도구가 한 글자 차이로 실패를 내면,
    # 그건 회귀 탐지가 아니라 도구가 명세를 안 읽은 것이다.
    # 고정 제목 절은 여전히 문자 그대로 일치해야 한다 — 거기선 제목이 곧 식별자다.
    b_h2, c_h2 = base["structure"]["h2"], cand["structure"]["h2"]
    fixed = set(base.get("fixed_headings") or cand.get("fixed_headings") or [])
    b_fixed = [x for x in b_h2 if x in fixed]
    c_fixed = [x for x in c_h2 if x in fixed]
    free_drift = [(b, c) for b, c in zip(b_h2, c_h2) if b != c and b not in fixed]
    # **h2 개수 동일을 요구하지 않는다.** 고정 제목이 없는 명세에서는 그 요구가
    # 사실상 "절을 정확히 N개 써라"가 되어, 명세가 조건부로 열어 둔 절을 빼는 판단
    # (SP8: 조건부 절의 생략은 판단이지 누락이 아니다)과 정면으로 부딪힌다.
    # 실제로 집필자가 "절을 하나 더 나눌까"를 내용이 아니라 **카운터 맞추기**로 결정했다.
    #
    # 대신 명세가 필수로 정한 것이 있는지를 본다. 개수 변화는 보고만 한다 —
    # 조건부 절을 왜 뺐는지는 게이트 보고가 받고, 최종 판단은 사람이 한다.
    required_missing = (cand.get("spec_conformance") or {}).get("missing", [])
    ok = (b_fixed == c_fixed and not required_missing
          and all(b == c for b, c in zip(b_h2, c_h2) if b in fixed))
    r["detail"]["structure"] = {
        "baseline": b_h2, "candidate": c_h2,
        "h2_count": [len(b_h2), len(c_h2)],
        "required_missing": required_missing,
        "missing": [x for x in b_h2 if x not in c_h2],
        "added": [x for x in c_h2 if x not in b_h2],
        "fixed_headings_ok": b_fixed == c_fixed,
        "free_heading_drift": [{"baseline": b, "candidate": c} for b, c in free_drift],
        "order_same": [x for x in b_h2 if x in fixed] == [x for x in c_h2 if x in fixed],
    }
    r["verdict"]["구성"] = "통과" if ok else "실패"

    # 내용 — 빠진 것이 실패다. 늘어난 것은 보고만 한다(더 설명한 것일 수 있다)
    bc, cc = base["content"], cand["content"]
    lost_num = [x for x in bc["numbers"] if x not in cc["numbers"]]
    # 정규화 후 비교 — 표기 차이를 유실로 세지 않는다. 옛 기준값에 없으면 원본 표기로 폴백.
    b_cx = bc.get("complexities_norm") or [norm_complexity(x) for x in bc["complexities"]]
    c_cx = cc.get("complexities_norm") or [norm_complexity(x) for x in cc["complexities"]]
    lost_cx = [x for x in b_cx if x not in c_cx]
    lost_id = [x for x in bc["identifiers"] if x not in cc["identifiers"]]
    shrink = cc["prose_chars"] < bc["prose_chars"] * 0.8
    # 분량 배수 — 상한을 두지 않는다. 명세가 요구한 항목을 채우면 길어지는 게 정상이라
    # 숫자로 잘라 내면 오히려 요구를 못 채우게 된다. **10배를 넘을 때만 사람에게 묻는다.**
    ratio = cc["prose_chars"] / bc["prose_chars"] if bc["prose_chars"] else 0.0
    r["detail"]["content"] = {
        "lost_numbers": lost_num, "lost_complexities": lost_cx,
        "lost_identifiers": lost_id[:20], "lost_identifier_count": len(lost_id),
        "prose_chars": [bc["prose_chars"], cc["prose_chars"]],
        "prose_ratio": round(ratio, 2),
        "needs_length_confirm": ratio > 10,
        "code_blocks": [bc["code_blocks"], cc["code_blocks"]],
    }
    r["verdict"]["내용"] = "통과" if not (lost_cx or shrink) else "확인 필요"
    if ratio > 10:
        r["verdict"]["분량"] = "사용자 확인 필요"

    # 문체 — 동일이 아니라 악화 없음
    bg, cg = base["style"]["grade"], cand["style"]["grade"]
    r["detail"]["style"] = {"baseline": bg, "candidate": cg,
                            "codes_baseline": base["style"]["codes"],
                            "codes_candidate": cand["style"]["codes"]}
    r["verdict"]["문체"] = "통과" if GRADE.get(cg, 0) >= GRADE.get(bg, 0) else "실패(악화)"

    # voice 준수 — 선언한 장치가 사라졌는지
    if "voice_compliance" in base and "voice_compliance" in cand:
        bt = base["voice_compliance"].get("device_traces", {})
        ct = cand["voice_compliance"].get("device_traces", {})
        # 흔적 탐지는 휴리스틱이라 1건 차이로 실패를 내면 오탐이 잦다.
        # **기준값에 뚜렷하게(2회 이상) 있던 장치가 아예 사라진 경우**만 실패로 본다.
        gone = [k for k, n in bt.items() if n >= 2 and ct.get(k, 0) == 0]
        thin = [k for k, n in bt.items() if n >= 2 and 0 < ct.get(k, 0) < n / 2]
        bh = base["voice_compliance"].get("register_hint", {})
        ch = cand["voice_compliance"].get("register_hint", {})
        # 종결 톤이 뒤집혔는가 — voice 이탈의 가장 굵은 신호다.
        flipped = (bh.get("존댓말_종결", 0) > bh.get("평서체_종결", 0)
                   and ch.get("존댓말_종결", 0) <= ch.get("평서체_종결", 0))
        r["detail"]["voice"] = {"baseline": bt, "candidate": ct,
                                "devices_gone": gone, "devices_thin": thin,
                                "register": [bh, ch], "register_flipped": flipped}
        r["verdict"]["voice 준수"] = "통과" if not gone and not flipped else "실패"

    r["overall"] = "통과" if all(v == "통과" for v in r["verdict"].values()) else "사람 확인 필요"
    return r


def cmd_measure(args) -> int:
    out = measure(Path(args.path), args.spec, Path(args.project or "."), args.voice)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_baseline(args) -> int:
    cfg = json.loads(Path(args.set).read_text(encoding="utf-8"))
    items = []
    for it in cfg["items"]:
        p = Path(it["file"]).expanduser()
        if not p.exists():
            print(f"  건너뜀(없음): {p}", file=sys.stderr)
            continue
        m = measure(p, it.get("spec"), Path(it.get("project", ".")).expanduser(), it.get("voice"))
        m["id"] = it["id"]
        m["accept"] = it.get("accept", [])
        m["reject"] = it.get("reject", [])
        items.append(m)
        print(f"  {it['id']:22s} {m['lines']:4d}줄  등급 {m['style']['grade']}  "
              f"h2 {len(m['structure']['h2'])}개")
    out = Path(args.out).expanduser()
    out.write_text(json.dumps({"schema_version": 1, "items": items},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n{len(items)}건 → {out}")
    return 0


def cmd_selfcheck(args) -> int:
    """집필자가 스스로 도는 점검. **기준값을 아예 만지지 않는다.**

    회귀의 독립성은 "원문을 보지 마라"는 지시로는 안 지켜진다 — 채점하려면 기준값을
    읽어야 하고 기준값에는 원문 구조가 들어 있다. 실제로 워커 둘이 그 경로로 원문
    목차를 봤고, 한 명은 "완전한 블라인드가 아니었다"고 스스로 보고했다.

    **분리가 답이다.** 집필자는 이 커맨드를 쓴다 — 명세와 voice 만 보고 자기 글을 잰다.
    기준값 대조는 채점자(오케스트레이터)가 따로 돌린다. 집필자에게 기준값 경로를
    주지 않으면 볼 방법 자체가 없다.
    """
    path = Path(args.file).expanduser()
    project = Path(args.project or ".").expanduser()
    m = measure(path, args.spec, project, args.voice)
    conf = m.get("spec_conformance") or {}
    vc = m.get("voice_compliance") or {}
    out = {
        "file": path.name,
        "문체등급": m["style"]["grade"],
        "적발": {"S1": m["style"]["s1"], "S2": m["style"]["s2"], "S3": m["style"]["s3"]},
        "코드": m["style"]["codes"],
        "필수절_누락": conf.get("missing", []),
        "h2": len(m["structure"]["h2"]),
        "산문자수": m["content"]["prose_chars"],
        "장치_흔적": vc.get("device_traces", {}),
        "사람이_봐야_할_장치": vc.get("manual_check_devices", []),
        "그림없이_이어진_산문_최장": vc.get("max_prose_run_without_visual"),
        "종결톤": vc.get("register_hint", {}),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    bad = m["style"]["s1"] > 0 or conf.get("missing")
    return 1 if bad else 0


def cmd_compare(args) -> int:
    base_all = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base = next((x for x in base_all["items"] if x["id"] == args.id), None)
    if not base:
        print(f"기준값에 '{args.id}' 가 없다", file=sys.stderr)
        return 2
    cand = measure(Path(args.candidate), base.get("spec"),
                   Path(args.project or "."), base.get("voice"))
    r = compare(base, cand)
    if getattr(args, "brief", False):
        # 집필자가 스스로 돌릴 때 쓴다. **기준값의 목차·식별자를 찍지 않는다** —
        # "원문을 보지 마라"고 해 놓고 채점 명령이 원문 구조를 노출하면 그 지시가 무의미해진다.
        # 판정과 수치 차이만 준다. 무엇을 고쳐야 하는지는 그것으로 충분하다.
        c = r["detail"]["content"]; st = r["detail"]["structure"]
        brief = {
            "id": r["id"], "verdict": r["verdict"], "overall": r["overall"],
            "산문비": c["prose_ratio"], "필수절_누락": st["required_missing"],
            "문체": r["detail"]["style"]["candidate"],
            "사라진_장치": r["detail"].get("voice", {}).get("devices_gone", []),
            # 기계가 못 재는 장치는 **통과로 세지 않고 이름을 그대로 넘긴다.**
            # 이걸 안 찍으면 voice 항목이 공허하게 통과한 것을 아무도 모른다.
            "사람이_봐야_할_장치": (cand.get("voice_compliance") or {}).get("manual_check_devices", []),
        }
        print(json.dumps(brief, ensure_ascii=False, indent=2))
        return 0
    print(json.dumps(r, ensure_ascii=False, indent=2))
    print("\n" + "=" * 56)
    for k, v in r["verdict"].items():
        print(f"  {k:10s} {v}")
    print(f"\n  종합: {r['overall']}")
    if base.get("accept") or base.get("reject"):
        print("\n  사람이 볼 것 —")
        for a in base.get("accept", []):
            print(f"    수용: {a}")
        for x in base.get("reject", []):
            print(f"    불수용: {x}")
    return 0 if r["overall"] == "통과" else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("measure"); m.add_argument("path")
    m.add_argument("--spec"); m.add_argument("--project"); m.add_argument("--voice")
    m.set_defaults(func=cmd_measure)

    b = sub.add_parser("baseline"); b.add_argument("--set", required=True)
    b.add_argument("--out", default="GOLDEN_BASELINE.json"); b.set_defaults(func=cmd_baseline)

    sc = sub.add_parser("selfcheck",
                        help="집필자 자가 점검 — 기준값을 만지지 않는다(회귀 독립성)")
    sc.add_argument("file"); sc.add_argument("--spec"); sc.add_argument("--voice")
    sc.add_argument("--project"); sc.set_defaults(func=cmd_selfcheck)

    c = sub.add_parser("compare"); c.add_argument("--baseline", required=True)
    c.add_argument("--candidate", required=True); c.add_argument("--id", required=True)
    c.add_argument("--brief", action="store_true",
                   help="기준값 구조를 노출하지 않고 판정만 — 집필자 자가 점검용")
    c.add_argument("--project"); c.set_defaults(func=cmd_compare)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
