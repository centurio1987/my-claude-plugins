#!/usr/bin/env python3
"""AI 문체(기계 리듬) 정량 스캐너.

`L0_MACHINE_RHYTHM.md` Part A 중 **기계적으로 셀 수 있는 항목만** 센다.
상투 구조(F범주)·3의 법칙(R4)·품사 편중(R6)은 판단이 필요하므로 사람(에이전트)이 본문을 읽고 채운다.

**voice 를 인지한다.** `--voice <id>` 를 주면 그 퍼소나가 선언한 면제 코드를 등급에서 뺀다.
어떤 리듬을 자기 색으로 삼을지는 퍼소나의 권리이고, 면제된 코드를 세면 목소리가 있는 글일수록
점수가 나빠지는 뒤집힌 판정이 된다.

    python3 scan_ai_style.py <파일>                    # 스캔 + 등급
    python3 scan_ai_style.py <파일> --voice tony       # 면제 반영
    python3 scan_ai_style.py <파일> --json             # 기계 판독용
    python3 scan_ai_style.py <원본> --diff <윤문본>      # 수정률 계산

의존성 없음(표준 라이브러리만). 원본: blog `humanize-post/scripts/scan_ai_style.py`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import style_registry as SR  # noqa: E402  — 어휘 목록의 단일 출처

# ---------------------------------------------------------------------------
# 1. 제외 구간 — 마커·코드·frontmatter는 스캔 대상이 아니다
# ---------------------------------------------------------------------------

SCAFFOLD_HEADINGS = ("## 플롯 후보", "## 선택한 플롯", "## 주의사항")

# 인라인 코드가 있던 자리. 공백·쉼표가 없는 한 덩어리라 어절 하나로 센다.
CODE_SLOT = "⟨코드⟩"


def strip_non_prose(text: str) -> str:
    """frontmatter·코드펜스·viz/figure·밈 마커·JSX·import·스캐폴드를 제거한다."""
    # frontmatter
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    # 코드 펜스 전체 (```viz / ```figure / ```ts 등 모두)
    text = re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)
    # 레거시 마커
    text = re.sub(r"\[\[\[.*?\]\]\]", "", text, flags=re.S)
    text = re.sub(r"<<meme:.*?>>", "", text, flags=re.S)
    # import 문 / JSX 컴포넌트 태그
    text = re.sub(r"^import .*$", "", text, flags=re.M)
    text = re.sub(r"</?[A-Z][\w.]*[^>]*/?>", "", text)
    # MDX 의 ESM export 블록(`export const steps = [...]`) — **데이터지 산문이 아니다.**
    # 안 걷어내면 시뮬 프레임의 `title`·`detail` 문자열이 문단 하나로 잡혀 줄표가 P2 로,
    # 어미가 R1b 로 걸린다. 명세가 강제하는 산출물이 문체 규칙에 걸리는 구조라, 집필자가
    # 데이터의 문자열을 문체 때문에 고치게 된다 — 세는 단위가 틀린 것이다.
    # 골든셋 회귀 2·3라운드에서 두 워커가 연달아 같은 지점을 지적했다.
    # 닫는 괄호 줄(`];` `}` `)`)까지 삼킨다 — 안 그러면 `];` 하나가 문단으로 남아 수를 흔든다.
    text = re.sub(r"^export\s+(?:const|let|var|function|default)\b.*?(?=^[^\s\]\})]|\Z)",
                  "", text, flags=re.S | re.M)
    # 인라인 코드 — 지우지 말고 자리표로 바꾼다.
    # 통째로 지우면 `a`, `b`, `c` 가 ", , " 로 남아 스니펫이 판독 불가가 되고,
    # 절 구조가 무너져 is_parallel()/is_enumeration() 판정도 어긋난다.
    text = re.sub(r"`[^`\n]+`", CODE_SLOT, text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    # 스캐폴드 섹션은 해당 헤딩부터 다음 H2까지 잘라낸다
    for head in SCAFFOLD_HEADINGS:
        text = re.sub(
            rf"^{re.escape(head)}.*?(?=^## |\Z)", "", text, flags=re.S | re.M
        )
    return text


def split_blocks(text: str) -> tuple[list[str], list[str]]:
    """(산문 문단, 목록 줄) 로 나눈다. 인용(>)·표(|)·헤딩은 산문에서 제외."""
    paragraphs: list[str] = []
    bullets: list[str] = []
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block:
            continue
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if all(ln.startswith(">") for ln in lines):  # 인용 블록 — 원문 보호
            continue
        if all(ln.startswith("|") for ln in lines):  # 표
            continue
        # **줄 단위로 가른다.** 블록 전체가 불릿일 때만 목록으로 세면,
        # `**라벨**` 한 줄 뒤에 빈 줄 없이 불릿이 붙은 블록이 통째로 산문 문단이 되고
        # 그 불릿들의 쉼표가 전부 P1(쉼표 과다) 로 계산된다. 실제로 링크 목록 하나가
        # 등급을 A 에서 C 로 떨어뜨렸고, **빈 줄 하나를 넣으면 A 로 돌아왔다** —
        # 문장이 아니라 서식이 등급을 흔드는 자리였다.
        run: list[str] = []
        for ln in lines:
            if ln.startswith("#"):
                continue
            if re.match(r"^([-*+]|\d+\.)\s", ln):
                if run:
                    paragraphs.append(" ".join(run)); run = []
                bullets.append(ln)
            else:
                run.append(ln)
        if run:
            paragraphs.append(" ".join(run))
    return paragraphs, bullets


def split_sentences(paragraph: str) -> list[str]:
    parts = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", paragraph) if s.strip()]
    return [p for p in parts if len(p) > 1]


# ---------------------------------------------------------------------------
# 2. 패턴 사전 — AI_KOREAN_PATTERNS.md Part A 와 코드가 1:1 대응한다
# ---------------------------------------------------------------------------

# **어휘 목록은 여기 없다.** 문체 설정 카탈로그(`assets/style/lexicon.json`)에서 `l0.scanner`
# 코드가 붙은 항목을 읽는다. 예전에는 이 파일에 목록이 하드코딩돼 있어 사용자가 손댈 수 없었고,
# 편집기에서 바꾼 가중치가 스캐너에 닿지 않았다. 지금은 한 벌만 있다.
#
# 여기 남은 것은 **코드의 이름표**뿐이다. 무엇을 셀지는 카탈로그가, 어떻게 셀지는 이 파일이 정한다.
#
# `수 있다` 는 한국어에서 **가능성**(추측)이기도 하고 **능력**(사실)이기도 하다.
# "이 API 로 파일을 읽을 수 있습니다" 는 헤지가 아니라 기능 서술이다. 그래서 H1 꼬리에는
# 계사(`이다`)에 붙는 `일 수 / 될 수` 만 넣었다 — "X 일 수 있습니다" = "X 일지도 모른다".
W_LABELS: dict[str, str] = {
    "W1": "빈 상찬 — 역할·필수",
    "W2": "빈 상찬 — 함의",
    "W3": "섹션 예고",
    "W4": "~에 있어서",
    "W5": "무근거 수량",
    "W6": "단정 회피",
    "W7": "측정 불가 부사",
    "W8": "도입 상투구",
}

# 코드별 유효 어휘. 기본은 플러그인 카탈로그만 — `--voice` 를 주면 전역·voice 설정이 겹친다.
LEX: dict[str, list[dict]] = SR.l0_lists()


def lex_words(code: str) -> list[str]:
    """코드에 걸린 표면형 목록. 카탈로그 순서를 지킨다."""
    out: list[str] = []
    for x in LEX.get(code, []):
        for f in x.get("forms", []):
            if f not in out:
                out.append(f)
    return out


def regex_items(code: str) -> list[tuple[re.Pattern, re.Pattern | None, str]]:
    """정규식으로 정의된 항목 — (패턴, 예외 문맥, 교정 힌트)."""
    return [(re.compile(x["regex"]), re.compile(x["except"]) if x.get("except") else None, x.get("note", ""))
            for x in LEX.get(code, []) if x.get("regex")]

# 따옴표 덩어리를 명사처럼 문장에 끼워 넣는 버릇 — `"X"라는 Y`, `"X"처럼 보이는`.
# 규칙 원문은 NATURAL_KOREAN_GUIDE §D4(저자 직접 지적). 여기서는 기계 탐지만 맡고
# 교정은 review-post 소관이라 보고에 그렇게 적어 넘긴다.
QUOTE_NOUN = re.compile(r'"[^"\n]{2,40}"\s*(?:이?라는|처럼|으로|로|라고 하는|이라고)')

# 과장 은유·전투 어휘·완곡어법 무시 — NATURAL_KOREAN_GUIDE §D5·§D6(저자 직접 지적).
# 실제로 파괴·공격이 일어나는 대목에서는 정당하므로 **판단이 필요한 후보**로만 올린다.
# 목록은 카탈로그의 D6 항목. 어절 안에 파묻힌 우연한 일치를 막는다 — `약속이지`가 `속이지`로
# 잡혔던 오탐. 한국어에 \b가 없으므로 "앞 글자가 한글이 아니어야 한다"로 어절 머리를 판정한다.
def overwrought_re() -> dict[str, re.Pattern]:
    return {w: re.compile(r"(?<![가-힣])" + re.escape(w)) for w in lex_words("D6")}


def wa_chains(sentence: str) -> list[str]:
    """`A와 B와 C` — 명사 셋 이상을 접속조사로만 이은 사슬을 찾는다.

    정규식 하나로는 안 된다. 항목이 두 어절 이상이면(`flow control과`) 와/과가
    연속 어절에 오지 않기 때문이다. 그래서 와/과로 끝나는 어절의 **위치**를 모아
    2어절 이내로 인접한 것만 사슬로 묶는다(멀리 떨어진 둘은 별개 짝이다).
    """
    out: list[str] = []
    for clause in re.split(r"[,.]", sentence):
        words = clause.split()
        idx = [i for i, w in enumerate(words) if len(w) > 1 and w[-1] in ("와", "과")]
        run: list[int] = []
        for a, b in zip(idx, idx[1:]):
            if b - a <= 2:
                run = [a, b] if not run else run + [b]
            else:
                if len(run) >= 2:
                    out.append(" ".join(words[run[0] : run[-1] + 2]))
                run = []
        if len(run) >= 2:
            out.append(" ".join(words[run[0] : run[-1] + 2]))
    return out

# Part B — 저자 색. 어떤 패턴 목록에도 넣지 않는다 (STYLE_GUIDE Part 1). 보고용 리마인더.
# 이 자리에는 원래 특정 저자의 연결어·마무리 표현이 하드코딩돼 있었다.
# 스캐너가 한 사람의 어휘를 알고 있으면 다른 퍼소나의 글을 잴 때 그 사람 기준이 새어 나간다.
# 지금은 --voice 로 받은 퍼소나의 lexicon 에서 온다. 없으면 비어 있는 게 정상이다.
PROTECTED: list[str] = []

# 화살표(→ ← ⇒)·수학 기호는 기술 글의 정상 표기다. 이모지 블록만 잡는다.
EMOJI = re.compile(
    "[" "\U0001F300-\U0001FAFF" "\U0001F900-\U0001F9FF" "\U00002600-\U000026FF"
    "\U00002700-\U000027BF" "\U0001F1E6-\U0001F1FF" "\U0000FE0F" "]"
)
# 기호 **자체를 설명하는** 자리는 장식이 아니다 — `♭ 기호가 …를 뜻한다` 처럼 그 기호가
# 문장의 화제일 때. 같은 줄에 `기호`·`표기`·`문자`·`심볼` 이 있으면 세지 않는다.
SYMBOL_TALK = re.compile(r"기호|표기|문자|심볼")


@dataclass
class Finding:
    code: str
    severity: str  # S1 / S2 / S3
    label: str
    count: int
    where: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 3. 스캐너
# ---------------------------------------------------------------------------


def snippet(s: str, n: int = 46) -> str:
    s = " ".join(s.split())
    return s if len(s) <= n else s[:n] + "…"


# 첫 어절에 붙어 병렬을 만드는 조사. `HTTP는 ~, DNS는 ~, SMTP는 ~` 처럼
# 어절 자체는 다른데 조사만 겹치는 병렬을 잡으려고 쓴다.
PARALLEL_PARTICLES = ("은", "는", "이", "가", "을", "를", "도", "만", "에")

# 명사구가 아니라 용언이 활용된 절임을 알리는 꼬리. 나열 판정에서 제외하는 데 쓴다.
VERBAL_TAIL = re.compile(
    r"(니다|습니다|죠|고요|까요|십시오|세요|하고|이고|고|며|거나|지만|어서|아서|는데|면서)$"
)

# 부사격 조사로 끝나는 구 = 나열 항목이 아니라 문장 성분. 두 글자짜리만 쓴다 —
# `로`·`과` 같은 한 글자를 넣으면 `경로`·`결과` 같은 멀쩡한 명사가 걸린다.
ADVERBIAL_TAIL = re.compile(r"(에서|으로|에게|부터|까지|처럼|보다|로서|로써|한테|만큼)$")


def _head_particle(clause: str) -> str:
    """절 첫 어절의 끝 조사. 없으면 빈 문자열."""
    words = clause.split()
    if not words:
        return ""
    return words[0][-1] if words[0][-1] in PARALLEL_PARTICLES else ""


def is_parallel(sentence: str) -> bool:
    """병렬·점층 구조인가 — 저자 색(STYLE_GUIDE F2, PATTERNS Part B-4)이므로 쉼표 적발에서 뺀다.

    판정 셋 중 하나면 수사로 본다:
      (a) 절들의 **끝 음절이 겹침** (~않고, ~않고)
      (b) 절들의 **첫 어절이 겹침** (심각한 ~, 심각한 ~)
      (c) 절들의 **첫 어절 조사가 겹침** (HTTP는 ~, DNS는 ~, SMTP는 ~)
          — 어절이 전부 다른 고유명사라 (b)로는 안 잡히는 대구를 위해 필요하다.
    """
    clauses = [c.strip() for c in sentence.split(",") if c.strip()]
    if len(clauses) < 3:
        return False
    tails = [c[-1] for c in clauses[:-1]]  # 마지막 절은 종결어미라 제외
    heads = [c.split()[0] for c in clauses if c.split()]
    if len(tails) != len(set(tails)) or len(heads) != len(set(heads)):
        return True
    particles = [p for p in (_head_particle(c) for c in clauses) if p]
    return len(particles) >= 3 and len(set(particles)) == 1


def is_enumeration(sentence: str) -> bool:
    """항목 나열인가 — 용어·명령어·부품을 쉼표로 잇는 것은 AI 리듬이 아니라 목록이다.

    `**관찰할 것** — link LED, 광 power, cable 규격, CRC error.` 같은 문장은
    쉼표가 다섯이어도 기계 냄새와 무관하다. 사람이 원래 그렇게 쓴다.

    판정: 쉼표로 끊긴 절이 3개 이상이고, 마지막 절을 뺀 항목들이 대부분
    **맨 명사로 끝나는 짧은 구**(4어절 이하)면 나열로 본다.

    부사격 조사로 끝나는 항목(`~환경에서`, `~방식으로`)은 나열이 아니라 문장 성분이다.
    그걸 빼지 않으면 "그 결과, 우리는 다양한 환경에서, 여러 방식으로, ~했습니다" 같은
    **진짜 쉼표 남발**이 나열로 오인돼 빠져나간다.
    """
    clauses = [c.strip() for c in sentence.split(",") if c.strip()]
    if len(clauses) < 3:
        return False
    items = clauses[:-1]  # 마지막 절만 서술어를 달고 끝나는 게 보통이다
    nounish = [
        c
        for c in items
        if len(c.split()) <= 4
        and not VERBAL_TAIL.search(c)
        and not ADVERBIAL_TAIL.search(c)
    ]
    return len(nounish) / len(items) >= 0.6


PAREN_SPAN = re.compile(r"\([^()\n]{0,120}\)")


def commas_outside_parens(s: str) -> int:
    """괄호 밖 쉼표만 센다.

    `C2`(약어 첫 등장 풀어쓰기)를 지키면 `(Domain Driven Design, 도메인 주도 설계)` 같은
    글로스가 생기는데, 그 쉼표를 절 연결로 세면 **두 L0 규칙이 서로를 위반하게 만든다.**
    실제로 글로스 10개를 넣자 등급이 A에서 C로 떨어졌다. 괄호 안은 삽입된 부연이지
    문장을 이어 붙인 리듬이 아니라서, P1 이 겨냥하는 대상이 아니다.
    """
    return PAREN_SPAN.sub("", s).count(",")


def scan(raw: str, waived: set[str] | None = None) -> dict:
    text = strip_non_prose(raw)
    paragraphs, bullets = split_blocks(text)
    findings: list[Finding] = []

    all_sentences: list[str] = []
    for p in paragraphs:
        all_sentences.extend(split_sentences(p))
    n_sent = max(len(all_sentences), 1)

    # 어휘 스캔 범위 — 헤딩·표·인용(>)은 split_blocks가 이미 뺐다.
    para_text = "\n".join(paragraphs)          # 산문만 (D범주용)
    body_text = "\n".join(paragraphs + bullets)  # 산문 + 목록 (W·P범주용)

    # --- P1 쉼표 과다 (S1) ---------------------------------------------------
    hot = []
    for i, p in enumerate(paragraphs, 1):
        sents = split_sentences(p)
        if not sents:
            continue
        # 병렬·점층(Part B-4)과 항목 나열의 쉼표는 기계 리듬이 아니므로 밀도에서 뺀다.
        commas = sum(
            commas_outside_parens(s) for s in sents
            if not (is_parallel(s) or is_enumeration(s))
        )
        density = commas / len(sents)
        if density > 1.5:
            hot.append(f"문단 {i} 밀도 (문장당 {density:.1f}개): {snippet(p)}")
    for s in all_sentences:  # 문장 단위: 쉼표 3개 이상 (병렬·나열은 제외)
        n = commas_outside_parens(s)
        if n >= 3 and not (is_parallel(s) or is_enumeration(s)):
            hot.append(f"문장 내 쉼표 {n}개: {snippet(s)}")
    if hot:
        findings.append(Finding("P1", "S1", "쉼표 과다", len(hot), hot[:6]))

    # --- P2 줄표·콜론 남용 (S2) ---------------------------------------------
    # 짝을 이룬 삽입구(`— 부연 —`)는 줄표를 두 번 쓴 게 아니라 한 번 삽입한 것이다.
    # 세는 단위는 문자가 아니라 **용법**이라, 짝 하나를 1회로 친다.
    # 문장 끝(.!?)을 건너뛰면 삽입구가 아니라 서로 다른 두 번의 사용이다.
    DASH_PAIR = re.compile(r"[—–][^—–\n.!?]{1,80}[—–]")
    dash_paras = [
        f"문단 {i}: {snippet(p)}"
        for i, p in enumerate(paragraphs, 1)
        if (p.count("—") + p.count("–")) - len(DASH_PAIR.findall(p)) >= 2
    ]
    if dash_paras:
        findings.append(Finding("P2", "S2", "줄표 남용", len(dash_paras), dash_paras))

    # --- P3 이모지 (S1) ------------------------------------------------------
    emojis = [e for line in body_text.splitlines() for e in EMOJI.findall(line)
              if not SYMBOL_TALK.search(line)]
    if emojis:
        findings.append(Finding("P3", "S1", "본문 이모지", len(emojis), [", ".join(sorted(set(emojis))[:10])]))

    # --- P4 느낌표·물결 (S3) -------------------------------------------------
    # 한국어에서 `0~1023`, `32768~60999` 의 물결표는 어미가 아니라 **범위 기호**다.
    # 숫자에 끼인 물결을 빼고 센다 — 기술 글에서 이게 P4의 주된 오탐이었다.
    RANGE_TILDE = re.compile(r"(?<=[\d\w])~(?=[\d\w])")
    bangs = []
    for i, p in enumerate(paragraphs, 1):
        n_tilde = p.count("~") - len(RANGE_TILDE.findall(p))
        if p.count("!") + n_tilde >= 2:
            bangs.append(f"문단 {i}: !{p.count('!')}개 ~{n_tilde}개")
    if bangs:
        findings.append(Finding("P4", "S3", "느낌표·물결 남발", len(bangs), bangs[:5]))

    # --- P5 볼드 융단폭격 (S2) ----------------------------------------------
    # 융단폭격은 **한 덩이의 산문 안**에서 볼드가 겹칠 때다. 목록에는 두 가지 오탐이 있다:
    #   (a) 항목 머리의 라벨 볼드(`- **원리**:`) — 강조가 아니라 항목 이름이라 세지 않는다.
    #   (b) 항목이 다섯이고 각 항목에 볼드가 하나면 블록 합계는 5지만 항목별로는 1이다.
    # 그래서 세는 단위를 문단이 아니라 **항목**으로 내린다. P1의 나열 예외와 같은 부류.
    LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
    LIST_HEAD = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+(\*\*[^*]+\*\*)")

    def bold_units(par: str) -> list[str]:
        """문단을 볼드를 셀 단위로 쪼갠다 — 목록이면 항목마다, 아니면 통째로."""
        units, cur = [], []
        for line in par.split("\n"):
            if LIST_ITEM.match(line):
                if cur:
                    units.append("\n".join(cur))
                cur = [LIST_HEAD.sub(lambda m: m.group(0).replace(m.group(1), ""), line)]
            else:
                cur.append(line)
        if cur:
            units.append("\n".join(cur))
        return units

    bold_paras = []
    for i, p in enumerate(paragraphs, 1):
        n_bold = max(
            (len(re.findall(r"\*\*[^*]+\*\*", u)) for u in bold_units(p)), default=0
        )
        if n_bold >= 3:
            bold_paras.append(f"문단 {i}: 볼드 {n_bold}개")
    if bold_paras:
        findings.append(Finding("P5", "S2", "볼드 과다(문단당 3+)", len(bold_paras), bold_paras))

    # --- R1a 어미 돌림노래 (S1) / R1b 종결형 단조 (S2) -----------------------
    runs, low_variety, mono = [], [], []
    for i, p in enumerate(paragraphs, 1):
        sents = split_sentences(p)
        stripped = [re.sub(r"[.!?…\s]+$", "", s).split() for s in sents]
        tails = [w[-1] if w else "" for w in stripped]
        # (a) 완전히 같은 종결 어절 3연속
        run = 1
        for a, b in zip(tails, tails[1:]):
            if a and a == b:
                run += 1
                if run == 3:
                    runs.append(f"문단 {i}: '{a}' 3연속")
            else:
                run = 1
        # (b) 문단 내 종결 어절 다양성
        if len(sents) >= 4 and len(set(tails)) / len(tails) < 0.5:
            low_variety.append(f"문단 {i}: 종결 어절 {len(set(tails))}종 / {len(tails)}문장")
        # (c) 종결형 자체가 4연속 평서 격식 — 단문 강타·의문·명사형이 없는 구간
        #     격식체 통일은 저자 색(Part B-8)이므로 S2로만 본다.
        forms = ["니다" if t.endswith("니다") else ("다" if t.endswith("다") else "기타") for t in tails]
        run = 1
        for a, b in zip(forms, forms[1:]):
            if a == b and a != "기타":
                run += 1
                if run == 4:
                    mono.append(f"문단 {i}: '{a}' 종결 4연속 — 리듬 변주 없음")
            else:
                run = 1
    if runs or low_variety:
        findings.append(
            Finding("R1a", "S1", "어미 돌림노래", len(runs) + len(low_variety), runs + low_variety)
        )
    if mono:
        findings.append(Finding("R1b", "S2", "종결형 단조(4연속)", len(mono), mono))

    # --- R2 문장 길이 평준화 (S2) -------------------------------------------
    flat = []
    for i, p in enumerate(paragraphs, 1):
        lens = [len(s) for s in split_sentences(p)]
        if len(lens) >= 4 and min(lens) and max(lens) / min(lens) < 2.0:
            flat.append(f"문단 {i}: 길이 {min(lens)}~{max(lens)}자 (단문 강타 없음)")
    if flat:
        findings.append(Finding("R2", "S2", "문장 길이 평준화", len(flat), flat))

    # --- R8 접속조사 연쇄 (S2) ----------------------------------------------
    # P1(쉼표 과다)을 고치겠다고 나열 쉼표를 `와/과`로 이어 붙이면 쉼표 카운터는
    # 내려가지만 한국어는 더 나빠진다("A와 B와 C와 D"). 지표만 만족시키는 교정을
    # 막으려고 반대 방향에서 같이 잰다. 3연쇄부터 적발.
    chains = []
    for s in all_sentences:
        for c in wa_chains(s):
            chains.append(f"{c.count('와') + c.count('과')}연쇄: {snippet(c, 40)}")
    if chains:
        findings.append(Finding("R8", "S2", "접속조사(와/과) 연쇄", len(chains), chains[:5]))

    # --- R3 문단 길이 평준화 (S3) --------------------------------------------
    counts = [len(split_sentences(p)) for p in paragraphs]
    if len(counts) >= 5 and all(3 <= c <= 4 for c in counts):
        findings.append(
            Finding("R3", "S3", "문단 길이 평준화", len(counts), [f"{len(counts)}문단 전부 3~4문장 — 한 줄짜리 문단이 없음"])
        )

    # --- R5 불릿 과의존 (S2) ------------------------------------------------
    prose_lines = sum(len(split_sentences(p)) for p in paragraphs)
    total = prose_lines + len(bullets)
    if total and len(bullets) / total > 1 / 3:
        findings.append(
            Finding("R5", "S2", "불릿 과의존", len(bullets), [f"목록 {len(bullets)}줄 / 전체 {total}단위 ({len(bullets)/total:.0%})"])
        )

    # --- W 버즈워드 ---------------------------------------------------------
    # voice 가 자기 어휘로 올린 항목(가중치 양수·꺼짐)은 LEX 에서 이미 빠졌다(항목 단위 면제).
    # 근처에 있다고 적발을 지우지는 않는다.
    for code, label in W_LABELS.items():
        hits = []
        for w in lex_words(code):
            for m in re.finditer(re.escape(w), body_text):
                ctx = body_text[max(0, m.start() - 20) : m.end() + 20]
                hits.append(f"'{w}' … {snippet(ctx, 40)}")
        sev = "S1" if code in ("W1", "W2", "W8") else ("S3" if code == "W7" else "S2")
        limit = 1 if sev == "S1" else 2
        if len(hits) >= limit:
            findings.append(Finding(code, sev, label, len(hits), hits[:5]))

    # --- D7 승부 비유 (S2) --------------------------------------------------
    # `이긴다`·`이깁니다` 는 **실제로 겨룰 때만** 쓴다. 규칙이 값을 하나 정하는 상황
    # (우선순위 표·longest prefix match·설정 병합)에는 겨루는 주체가 없다.
    #
    # 이 규칙은 사용자가 명시적으로 준 피드백인데 **이관 중에 유실됐다** —
    # 구 `STYLE_GUIDE` R8 의 금지 목록에 있었으나 인벤토리에 "출처 없는 단정·덤프·반복
    # 금지"로만 요약돼 옮겨졌다. 그 결과 새로 쓴 글 셋이 같은 표현을 다시 썼다.
    # **기계가 잡지 않으면 또 샌다.** 그래서 여기 둔다.
    #
    # 국면을 가리키는 비유("진짜 승부처")는 저자 의도라 예외다 — 주어가 서로 겨루는지가
    # 가르는 기준인데 정규식은 그걸 못 본다. 그래서 S2 로 두고 사람이 판정한다.
    # D7~D11 의 패턴·예외 문맥·교정 힌트는 카탈로그 항목에 있다(`l0.scanner`).
    # 예외 문맥이 필요한 이유: `축`은 좌표·회전·시간축에서, 가격어는 실제 청구 금액에서 정상이다.
    # 정규식은 주어가 서로 겨루는지를 못 보므로 전부 S2 로 두고 사람이 판정한다.
    for code, label in (("D7", "승부 비유"), ("D8", "지형 은유"), ("D9", "축 오용"),
                        ("D10", "못 박다"), ("D11", "가격 비유")):
        hits, hints = [], []
        for rx, exc, hint in regex_items(code):
            hits += [snippet(x) for x in all_sentences if rx.search(x) and not (exc and exc.search(x))]
            if hint and hint not in hints:
                hints.append(hint)
        if hits:
            findings.append(Finding(code, "S2", label, len(hits), hits[:4 if code == "D7" else 3] + hints))

    # --- H1 헤지 중첩 (S1) --------------------------------------------------
    stacked = []
    for s in all_sentences:
        n = sum(s.count(t) for t in lex_words("H1"))
        if n >= 2:
            stacked.append(snippet(s))
    if stacked:
        findings.append(Finding("H1", "S1", "헤지 중첩", len(stacked), stacked[:5]))

    # --- H2 추측 어미 / H3 문두 완충 (S2) ------------------------------------
    # H2 — **완충어의 총량이 아니라 다양성을 센다.**
    #
    # 완충어를 일괄 금지하면 불확실한 것을 단정하게 되어 더 나쁘다. 규칙 문서는 근거
    # 수준별로 다른 형태를 쓰라고 정한다(연역·확실한 근거·근거의 신뢰도 유보·근거 부재·
    # 귀류법·논리적 추론). 자리마다 근거가 다른데 **표현이 하나뿐이면 수위를 맞춘 게
    # 아니라 습관**이다 — 그게 이 코드가 잡는 것이다.
    #
    # `보이다` 는 동사이기도 하다("표로 보입니다" = 드러난다). 구체 명사 뒤는 세지 않는다.
    HEDGE_VERB_OK = re.compile(
        r"(?:^|[\s(])[가-힣A-Za-z0-9]*(?:표|그래프|도식|그림|숫자|수치|형태|모양|색|선)으?로 보입니다")
    # 긴 꼴을 먼저 본다 — `인 것 같습니다` 가 `것 같습니다` 로 먼저 잡히면 형태 구분이 흐려진다.
    HEDGE_FORMS = sorted(lex_words("H2"), key=len, reverse=True)
    counts: dict[str, int] = {}
    for sent in all_sentences:
        if "로 보입니다" in sent and HEDGE_VERB_OK.search(sent):
            continue
        for form in HEDGE_FORMS:
            if form in sent:
                counts[form] = counts.get(form, 0) + 1
                break
    monotone = [f"`{k}` {n}회" for k, n in sorted(counts.items(), key=lambda x: -x[1]) if n >= 4]
    if monotone:
        findings.append(Finding(
            "H2", "S2", "완충 표현 단조", sum(counts[k.split('`')[1]] for k in monotone),
            monotone[:4] + ["근거 수준마다 다른 형태를 쓴다 — L0_MACHINE_RHYTHM §H 근거 수준 척도"]))
    h3 = [
        p.split()[0]
        for p in paragraphs + [s for s in all_sentences]
        if p.split() and p.split()[0].rstrip(",") in set(lex_words("H3"))
    ]
    if len(h3) >= 3:
        findings.append(Finding("H3", "S2", "문두 완충어", len(h3), [", ".join(sorted(set(h3)))]))

    # --- H4 양비론 마무리 (S1) ----------------------------------------------
    ambi = [snippet(s) for s in all_sentences if "물론" in s and ("지만" in s or "하지만" in s)]
    if ambi:
        findings.append(Finding("H4", "S1", "양비론 회피", len(ambi), ambi[:3]))

    # --- D1 문두 접속사 3연속 (S1) ------------------------------------------
    discourse_heads = set(lex_words("D1"))
    heads = [p.split()[0].rstrip(",") if p.split() else "" for p in paragraphs]
    run, seq = 1, []
    for i in range(1, len(heads)):
        if heads[i] in discourse_heads and heads[i - 1] in discourse_heads:
            run += 1
            if run >= 3:
                seq.append(f"문단 {i-1}~{i+1}: {heads[i-2]} / {heads[i-1]} / {heads[i]}")
        else:
            run = 1
    if seq:
        findings.append(Finding("D1", "S1", "문두 접속사 연속", len(seq), seq))

    # --- D2 / D3 / D4 — 산문 안에서만 본다 (목록 속 '첫째'는 정상 표기) ------
    # D2 는 이름 그대로 **문두**만 잡는다. `사실상의 표준`(de facto standard)은 굳어진
    # 명사구지 무논증 filler 가 아니라, 아무 데나 걸면 기술 글에서 통째로 오탐이 된다.
    d2 = "|".join(re.escape(w) for w in lex_words("D2")) or r"(?!)"
    D2_HEAD = re.compile(r"(?:^|[.!?]\s+|\n)\s*(" + d2 + r")(?!의)")
    for code, label, words, sev, limit in [
        ("D3", "산문 속 첫째/둘째", lex_words("D3"), "S2", 1),
        ("D4", "자기참조", lex_words("D4"), "S2", 2),
    ]:
        hits = [w for w in words for _ in re.finditer(re.escape(w), para_text)]
        if len(hits) >= limit:
            findings.append(Finding(code, sev, label, len(hits), [", ".join(sorted(set(hits)))]))

    d2_hits = [m.group(1) for m in D2_HEAD.finditer(para_text)]
    if len(d2_hits) >= 2:
        findings.append(
            Finding("D2", "S2", "무논증 문두", len(d2_hits), [", ".join(sorted(set(d2_hits)))])
        )

    # --- D5 인용 삽입 (S2) ---------------------------------------------------
    # 산문에서만 본다. 오해 목록(`1. **"…"** 반박`)은 bullets로 빠지므로 걸리지 않는다.
    quoted = [snippet(m.group(0), 44) for p in paragraphs for m in QUOTE_NOUN.finditer(p)]
    if quoted:
        findings.append(
            Finding("D5", "S2", "인용 삽입(→ review-post)", len(quoted), quoted[:5])
        )

    # --- D6 과장 은유 (S2) ---------------------------------------------------
    over = []
    for p in paragraphs:
        for w, rx in overwrought_re().items():
            m = rx.search(p)
            if m:
                over.append(
                    f"'{w}' … {snippet(p[max(0, m.start() - 18) : m.start() + 26], 42)}"
                )
    if over:
        findings.append(
            Finding("D6", "S2", "과장 은유(→ review-post)", len(over), over[:5])
        )

    # --- 등급 산정 -----------------------------------------------------------
    # 면제된 코드는 **등급 계산에서 뺀다.** 적발 목록에는 남겨 두되 표시만 한다 —
    # 무엇이 면제됐는지 안 보이면 면제가 옳은지 다시 볼 수 없다.
    waived = waived or set()
    for f in findings:
        if f.code in waived:
            f.label = f"{f.label}  [면제됨]"
    counted = [f for f in findings if f.code not in waived]
    s1 = sum(1 for f in counted if f.severity == "S1")
    s2 = sum(1 for f in counted if f.severity == "S2")
    if s1 == 0 and s2 <= 2:
        grade = "A"
    elif s1 == 0 and s2 <= 5:
        grade = "B"
    elif s1 <= 2:
        grade = "C"
    else:
        grade = "D"

    return {
        "grade": grade,
        "s1": s1,
        "s2": s2,
        "s3": sum(1 for f in counted if f.severity == "S3"),
        "waived": sorted(waived),
        "sentences": n_sent,
        "paragraphs": len(paragraphs),
        "findings": [f.__dict__ for f in findings],
    }


# ---------------------------------------------------------------------------
# 4. 수정률 (윤문 전/후 비교)
# ---------------------------------------------------------------------------


def edit_rate(before: str, after: str) -> dict:
    def sents(t: str) -> list[str]:
        ps, _ = split_blocks(strip_non_prose(t))
        out = []
        for p in ps:
            out.extend(" ".join(s.split()) for s in split_sentences(p))
        return out

    a, b = sents(before), sents(after)
    import difflib

    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    same = sum(block.size for block in sm.get_matching_blocks())
    total = max(len(a), 1)
    changed = total - same
    rate = changed / total
    verdict = "통과" if rate < 0.30 else ("⚠️ 경고 — diff 확인 권장" if rate <= 0.50 else "❌ 상한 초과 — 자동 적용 금지")
    return {"total_sentences": total, "changed": changed, "rate": rate, "verdict": verdict}


# ---------------------------------------------------------------------------


def render(path: str, r: dict) -> str:
    out = [f"# AI 문체 스캔: {path}", ""]
    out.append(f"자연스러움 등급: **{r['grade']}**  (적발 코드 수 — S1 {r['s1']}개 · S2 {r['s2']}개 · S3 {r['s3']}개)")
    out.append(f"산문 {r['paragraphs']}문단 / {r['sentences']}문장")
    out.append("")
    if not r["findings"]:
        out.append("적발 없음.")
    for f in sorted(r["findings"], key=lambda x: x["severity"]):
        out.append(f"## [{f['code']}] {f['label']} — {f['severity']} · {f['count']}건")
        for w in f["where"][:5]:
            out.append(f"  - {w}")
        out.append("")
    out.append("---")
    out.append("**판단이 필요해 스크립트가 못 잡는 항목** — 본문을 직접 읽고 채운다:")
    out.append("  F1~F4(상투 구조·마무리 공식), R4(3의 법칙 강박), R6(품사 편중), R7(대구 강박).")
    out.append("")
    if r.get("waived"):
        out.append("**이 voice 에서 면제된 코드**: " + " · ".join(r["waived"])
                   + " — 등급에서 뺐다. 고치려 들지 마라, 그게 저자의 색이다.")
    else:
        out.append("**적발 목록을 고치기 전 활성 voice 의 `axes`·`waivers` 와 대조한다.**")
        out.append("  `--voice <id>` 를 주면 면제가 자동 반영된다. 안 주면 면제 없이 잰다.")
    if PROTECTED:
        out.append("  이 voice 가 자기 어휘로 선언한 것: " + " / ".join(PROTECTED[:8]))
    return "\n".join(out)


def load_voice_context(voice_id: str) -> set[str]:
    """활성 voice 의 면제 코드를 읽고, 그 voice 의 어휘군을 PROTECTED 에 채운다.

    authoring.py 를 import 하지 않고 파일을 직접 읽는다 — 이 스캐너는 레지스트리가
    없는 환경(단독 실행·CI)에서도 돌아야 하고, 그때는 면제 없이 재는 게 맞다.
    """
    global PROTECTED, LEX
    f = SR.registry_home() / "voices" / voice_id / "voice.json"
    if not f.exists():
        print(f"# voice '{voice_id}' 를 찾지 못했다 ({f}) — 면제 없이 잰다.", file=sys.stderr)
        return set()
    v = json.loads(f.read_text(encoding="utf-8"))
    lex = v.get("axes", {}).get("lexicon", "")
    PROTECTED = re.findall(r"[`\u2018\u2019']([^`\u2018\u2019']{2,20})[`\u2018\u2019']", lex)
    # 문체 설정(전역 → voice)을 겹친 어휘 목록으로 갈아 끼운다. 양수로 올렸거나 끈 L0 항목은
    # 여기서 빠진다 — 코드 전체를 면제하는 `waivers` 보다 좁은, 항목 단위 면제다.
    # 검증을 통과하지 못한 설정은 **적용하지 않는다** — 사유 없는 항목 면제가 조용히 스며들 수 있다.
    problems = SR.validate_all_for(voice_id)
    if problems:
        print(f"# voice '{voice_id}' 의 문체 설정이 검증에 실패해 항목 면제를 적용하지 않는다:", file=sys.stderr)
        for p in problems[:5]:
            print(f"#   {p}", file=sys.stderr)
        LEX = SR.l0_lists()
        return {w["code"] for w in v.get("waivers", []) if w.get("code")}
    eff = SR.effective(voice_id)
    LEX = SR.l0_lists(eff)
    for x in eff["items"]:
        if x["active"] and x["weight"] > 0:
            PROTECTED.extend(f for f in x.get("forms", []) if f not in PROTECTED)
    return {w["code"] for w in v.get("waivers", []) if w.get("code")}


def prose_units(raw: str) -> tuple[list[str], list[list[str]]]:
    """가중치 어휘 스캔(`scan_lexicon.py`)이 쓰는 단위 — 산문 문단과 목록 줄, 문단별 문장.

    L0 스캐너와 **같은 잣대로** 산문을 가른다. 둘이 따로 자르면 같은 글에서 문장 수가 달라져
    허용량 계산이 어긋난다.
    """
    paragraphs, bullets = split_blocks(strip_non_prose(raw))
    units = paragraphs + [re.sub(r"^([-*+]|\d+\.)\s+", "", b) for b in bullets]
    return units, [split_sentences(u) or [u] for u in units]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--voice", help="활성 퍼소나 id — 면제 코드를 등급에서 뺀다")
    ap.add_argument("--diff", metavar="AFTER", help="윤문본 경로 — 수정률 계산")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    waived = load_voice_context(args.voice) if args.voice else set()
    raw = open(args.path, encoding="utf-8").read()

    if args.diff:
        res = edit_rate(raw, open(args.diff, encoding="utf-8").read())
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"수정률: {res['rate']:.0%} (문장 {res['total_sentences']}개 중 {res['changed']}개) — {res['verdict']}")
        return 0 if res["rate"] <= 0.50 else 1

    r = scan(raw, waived)
    print(json.dumps(r, ensure_ascii=False, indent=2) if args.json else render(args.path, r))
    return 0 if r["grade"] in ("A", "B") else 1


if __name__ == "__main__":
    sys.exit(main())
