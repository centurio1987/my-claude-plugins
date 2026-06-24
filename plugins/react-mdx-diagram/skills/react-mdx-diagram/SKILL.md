---
name: react-mdx-diagram
description: >-
  프로젝트별 theme과 디자인 시스템에 맞춰 MDX 안에 순수 React(외부 라이브러리·import 없는 inline-style) 다이어그램을
  그리는 스킬. 스킬이 한 프로젝트에서 처음 쓰일 때 1회 초기 세팅(theme 토큰 파일 + 디자인 시스템 바인딩)을 만들고, 이후 그
  profile을 재사용해 일관된 도식을 양산한다. 사용자가 "이 글/문서에 다이어그램/도식/개념도/아키텍처 그림 넣어줘", "react로
  다이어그램 만들어줘", "mdx에 그림 그려줘", "우리 디자인 시스템 스타일로 도식 만들어줘", "다이어그램 테마 세팅해줘", "before
  after 비교도/레이어 스택/플로우/아키텍처 그려줘" 같이 요청하거나, `.md`/`.mdx` 문서에 `(( ... ))` 플레이스홀더가 있어
  그림으로 채워야 하는 맥락이면 반드시 이 스킬을 사용한다. 디자인 시스템·Figma·디자인 토큰·컴포넌트 라이브러리를 주면서 그에 맞는
  도식을 원하면 특히 이 스킬을 쓴다. (구 mdx-concept-diagram을 대체한다 — `(( ))` 채우기도 이 스킬이 담당한다.)
  단순 텍스트 편집, Mermaid/차트 라이브러리 도입, PPT/PDF 변환에는 사용하지 않는다.
---

# React MDX Diagram

MDX 문서 안에 **외부 의존성 없는 순수 React 다이어그램**을 그리는 스킬이다. 두 가지를
한 흐름으로 처리한다: (1) 프로젝트마다 한 번 하는 **초기 세팅**으로 도식의 룩(theme)과
디자인 시스템 명명을 profile에 고정하고, (2) 그 profile을 재사용해 **일관된 도식을
작성**한다. 글에 남겨둔 `(( ... ))` 플레이스홀더를 채우는 작업도 여기 포함된다(구
`mdx-concept-diagram`을 흡수).

## 핵심 원칙

1. **자기완결 inline React.** React Flow·Mermaid·차트 라이브러리·아이콘 패키지를 쓰지
   않고, 프로젝트의 실제 컴포넌트도 import하지 않는다. 순수 JSX + inline `style={{}}` +
   flexbox/inline SVG로만 그려서 어떤 MDX 호스트에서도 설정 없이 렌더된다. **아이콘은
   인라인 SVG 벡터 글리프로 그린다 — 이모지·픽토그램(`✅ ⚠️ 💡 🔁 📦 🚀` 등)을 아이콘
   대용으로 쓰지 않는다.** 노드 의미 아이콘(person·external·container·database·queue)은
   `references/node-glyphs.md`의 SVG path를 `T.style.iconMode`(fill/line)에 맞춰
   그리고(canon의 `glyph` 헬퍼), 그 5종으로 표현이 안 되는 개념은 같은 `24×24`
   viewBox·동일 stroke 규칙으로 새 inline SVG 글리프를 직접 만든다. 방향·연결 표시에만
   단순 기하 마크(`→ ↓ ▼` 텍스트나 SVG `<marker>` 화살표)를 쓴다 — 의미를 담는 자리에는
   이모지가 아니라 SVG를 둔다. 디자인 시스템을 바인딩해도 이 규칙은 안 바뀐다 — 바뀌는
   건 토큰 값과 컴포넌트 이름뿐이다.
2. **렌더 가능성 — 대문자 하위 컴포넌트 태그를 쓰지 않는다.** 대문자 JSX 태그는 MDX
   호스트마다 깨지는 1순위 원인이다. (a) 표준 MDX는 스코프에 없는 대문자 태그를
   `Expected component 'X' to be defined`로 던지고, (b) 일부 호스트(특히 VS Code MDX
   프리뷰)는 보이는 모든 대문자 태그에 대해 컴포넌트 바인딩을 주입해서, 같은 스코프의
   local `const X`와 충돌해 `Identifier 'X' has already been declared`로 컴파일 자체가
   깨진다. 표준 `@mdx-js/mdx`로는 (b)가 재현되지 않으니 "내 환경에선 컴파일됨"은
   안전 보증이 아니다. 그래서 **이식성 있는 단 하나의 규칙**(구 스킬이 문제없이 쓰던
   패턴)을 따른다:
   - 파일 안의 대문자 JSX 태그는 **top-level 아키타입 컴포넌트뿐**이고, 본문(markdown)에서
     **컬럼 0**에 `<Archetype />`로만 쓴다.
   - 다이어그램 **내부**는 소문자 HTML 엘리먼트(`<div>`/`<span>`/`<pre>`)와 `.map()`으로
     만든다. 재사용 조각은 **소문자 헬퍼 함수**로 정의하고 **호출**로 쓴다 —
     `{panel(a)}` (절대 `<Panel/>` 태그로 쓰지 않는다).
   - 값 객체 `T`는 `<T>`로 안 쓰이고 `T.x` 값으로만 참조하므로 top-level이어도 안전하다.
   - 작성 후 `check_mdx.py`가 이 규칙 위반(중첩 대문자 태그)을 잡는다.
3. **theme 주도 일관성.** 한 문서의 모든 도식은 같은 팔레트·간격·타이포를 공유해 한
   세트처럼 보인다. 이를 위해 profile의 theme을 MDX 최상단 `export const T = {...}`로
   직렬화하고 모든 컴포넌트가 `T`에서 값을 읽는다. theme을 바꾸면 문서 전체가 따라온다.
4. **의미 기반 색.** 색은 장식이 아니라 의미다(문제=rose, 해결=green, 단계
   indigo→sky→green→amber, 구조=slate). 디자인 시스템의 brand/danger/success를 이
   의미 역할에 매핑한다.
5. **본문 사실에 충실.** 도식의 라벨·수치·관계는 문서/요청에서 추적 가능해야 한다.
   멋있어 보이려고 없는 단계나 수치를 지어내지 않는다.
6. **프로젝트 트리는 건드리지 않는다.** theme/binding 같은 상태는 스킬/플러그인 내부
   profile에 저장한다(사용자가 명시적으로 요청하지 않는 한 repo에 파일을 만들지 않는다).

## 스킨 프리셋 — 하나의 DNA, 세 가지 스킨

이 스킬은 다이어그램·시스템 아키텍처 디자인 시스템을 내장한다. **공통 DNA**(8색
파스텔 팔레트 · 5종 노드 의미체계 person·external·container·database·queue · C4
L1→L3 위계 · Helvetica Neue + JetBrains Mono 타이포)는 하나로 고정하고, **세 가지
스킨(theme 프리셋)** 으로 렌더한다:

| 프리셋 | 캔버스 | 성격 | 언제 |
|--------|--------|------|------|
| `candy-os`  | 다크 `#0B0B0B` | 솔리드 비비드 타일 · 블랙 글리프 · 밝은 볼드 커넥터 | 임팩트 있는 덱/표지 |
| `swiss`     | 라이트 `#ECEBE7` | 대형 볼드 라벨 · 파스텔 밴드 · 라인 아이콘 · 얇은 라인 | 에디토리얼/문서 |
| `blueprint` | 라이트 `#F4F3F0` | 파스텔 채움 + 볼드 블랙 키라인 · 직각 화살표 · `[type-tag]` | 아키텍처/C4 (기본값) |

세 스킨은 팔레트·노드 의미체계·C4 위계를 **동일하게** 담고, 캔버스·노드 테두리·아이콘
채움(fill) vs 라인·커넥터·타입태그·C4 중첩 표현 **방식만** 다르다. 전체 명세는
`references/style-guide.md`, 토큰 값은 `assets/theme.<skin>.ts`, 컴포넌트 작성법과
완성 예시는 `references/canon.md` + `assets/samples/reference.<skin>.mdx`에 있다.
프로젝트가 디자인 시스템을 바인딩하지 않았으면 `theme.default.ts`(= `blueprint`)를
쓴다.

## 작업 절차

### 0. profile 확인 (항상 먼저)
```bash
python3 <skill>/scripts/profile.py status
```
- `set_up: true` → 세팅 완료. 1단계 건너뛰고 `profile.py show`로 theme/binding을 읽어
  3단계로 간다.
- `set_up: false` → 이 프로젝트에서 처음 쓰는 것. **1단계(세팅)**를 한 번 한다.

### 1. 초기 세팅 (profile이 없을 때만, 1회)
`references/setup.md`를 읽고 따른다. 요지:
- **스킨 프리셋을 먼저 고른다** — `candy-os` / `swiss` / `blueprint` 중 글의 성격에
  맞는 것을 제안한다(위 표 참고, 기본 `blueprint`). 고른 스킨의
  `assets/theme.<skin>.ts`를 profile의 `theme.ts`로 복사한다.
- 사용자가 줄 수 있는 자료(디자인 토큰/theme 파일, repo 컴포넌트 라이브러리, Figma/
  스크린샷, 서술형 스펙, 디자인 시스템 repo URL)를 가볍게 묻되 **프리셋 그대로도 좋은
  선택지**로 제시한다. 자료가 없거나 원치 않으면 고른 프리셋(없으면
  `theme.default.ts` = `blueprint`)을 그대로 쓰고 진행한다.
- 자료를 받으면 `references/design-system-binding.md`에 따라 토큰을 추출해 `theme.ts`를
  만들고, 컴포넌트 라이브러리가 있으면 이름 매핑을 `binding.json`에 적는다.
- profile 위치는 `python3 <skill>/scripts/profile.py path`로 확인해 그 디렉터리에 쓴다.

### 2. 작성 의도 수집
- 일반 요청이면 본문/맥락을 읽고 무엇을 그릴지 정한다.
- `(( ... ))` 플레이스홀더가 있는 문서면 빠뜨리지 않게 전부 뽑는다:
  ```bash
  python3 <skill>/scripts/find_placeholders.py "<문서 경로>"
  ```
  각 마커의 `heading`/`text`를 보고 **그림 지시문**(무엇을 그릴지 설명 → 창작)인지
  **시각화할 내용**(이미 적힌 불릿/성과·한계 → 재구성)인지 분류한다.

### 3. 아키타입 선택 + 작성
`references/canon.md`를 읽고(컴포넌트 어휘·아키타입·theme-const 패턴) 의도에 맞는
아키타입을 고른다. 개념도용 6종 `BeforeAfter`·`LayerStack`·`FlowSteps`·`Architecture`·
`CardSet`·`Matrix`, 그리고 디자인 시스템의 아키텍처 5종 `Palette`·`NodeTaxonomy`·
`C4Hierarchy`·`C4Container`·`Flowchart`·`Sequence`(노드 의미체계·C4 위계·플로우/시퀀스).
막히면 `assets/samples/reference.<skin>.mdx`의 완성 예시를 베이스로 복제·수정한다. 그다음:
- MDX 최상단에 profile theme을 `export const T = {...}`로 직렬화(§6 토큰 shape 그대로,
  쓰는 색 패밀리만). 컴포넌트는 `T.node.*`·`T.c4.*`·`T.style.*`를 읽어 스킨에 따라
  분기한다(아이콘 fill/line, 노드 테두리, 타입태그 등).
- 데이터 주도로 작성: 내용을 컴포넌트 상단 객체 배열로 선언하고 `.map()`. 컴포넌트
  이름은 개념을 드러내는 PascalCase(`DomainModelBeforeAfter`).
- **다이어그램 내부는 소문자 HTML + `.map()`으로만 만든다**(원칙 2). 재사용 조각은
  **소문자 헬퍼 함수**로 정의하고 호출로 쓴다 — `const panel = (a) => (<div>…</div>)`를
  `{actors.map(a => panel(a))}`로. 대문자 하위 컴포넌트 태그(`<Panel/>`)는 쓰지 않는다.
- 디자인 시스템이 바인딩돼 있으면 이 **소문자 헬퍼 함수 이름**에 `binding.json`의
  `componentNames`를 camelCase로 적용한다(canon `Node`→그들의 `Card`면 `card` 헬퍼).
  코드가 그 팀 어휘로 읽히되 태그가 아니라 함수 호출이라 어디서든 렌더된다.
- top-level `export const`에는 값 객체 `T`와 아키타입 컴포넌트만 둔다. 본문에서는
  `<ArchetypeName />`를 **컬럼 0**에 한 줄로 쓴다(플레이스홀더면 `(( ))` 자리를 그 한 줄로
  치환). JSX 블록은 앞뒤 빈 줄로 분리.

### 4. 검증 (필수 게이트)
- **렌더 가능성 lint를 반드시 통과시킨다:**
  ```bash
  python3 <skill>/scripts/check_mdx.py "<출력 파일>"
  ```
  이 스크립트는 원칙 2 위반(다이어그램 내부의 대문자 하위 컴포넌트 태그)과 정의 없는
  본문 태그를 잡고, **원칙 1 위반(다이어그램 JSX 안에서 아이콘 대용으로 쓰인
  이모지·픽토그램)도 잡는다.** 대문자 태그 위반은 소문자 헬퍼 함수 호출(`{panel(a)}`)
  이나 inline 소문자 HTML로, 이모지 아이콘은 `node-glyphs.md`의 inline SVG 글리프로
  바꿔 **lint가 깨끗해질 때까지** 고친다(연결 화살표 `→ ▼` 같은 기하 마크는 통과한다.
  본문 산문에 이모지가 있어 나온 경고면 그 줄은 무시한다).
- 플레이스홀더 작업이면 `find_placeholders.py`를 **다시 돌려** 남은 `(( ))`가 0개인지
  확인.
- 모든 도식이 `T`에서 색을 읽어 한 세트로 보이는지 확인.
- **디자인 시스템 자체를 손보는 작업**(theme/canon/샘플 수정)이면 회귀 게이트를 돌린다:
  Playwright DNA 테스트(`cd tests && npm i && npm test` — 팔레트·노드 의미체계·C4·타이포·
  스킨 구분을 3개 스킨에 대해 검증)와 품질 체크리스트
  (`assets/QUALITY_CHECKLIST.md` → `scripts/score.py`, 기준 85/100·크리티컬 0점 금지).
  통과해야 완료로 본다.

## 출력 형태 예시

`(( before -> after 도메인 모델 설계도 ))` → 본문 자리는 `<DomainModelBeforeAfter />`
한 줄로 치환하고, 파일 최상단에:

```mdx
export const T = {
  surface: { canvas: '#f8fafc', border: '#e2e8f0' },
  problem:  { bg: '#fff1f2', border: '#fca5a5', text: '#7f1d1d', accent: '#dc2626' },
  solution: { bg: '#f0fdf4', border: '#86efac', text: '#14532d', accent: '#16a34a' },
  ink: { heading: '#1e293b', muted: '#94a3b8' },
  font: { sans: '-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif' },
}

export const DomainModelBeforeAfter = () => {
  const before = ['거대 Aggregate (단일 루트)', '도메인 메서드 폭증', 'Row Flooding']
  const after  = ['LCA / Process / Data 분리', '상호작용은 도메인 서비스로', '프로파일 + CQRS']
  // 소문자 헬퍼 함수 — JSX 태그가 아니라 호출({col(...)})로 쓴다.
  const col = (c, label, items) => (
    <div style={{ flex: 1, border: `2px solid ${c.border}`, borderRadius: 10, padding: 14, background: c.bg }}>
      <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: c.accent, marginBottom: 10 }}>{label}</div>
      {items.map((t, i) => (
        <div key={i} style={{ fontSize: 12, color: c.text, background: '#fff', border: `1px solid ${c.border}`, borderRadius: 6, padding: '8px 10px', marginBottom: 6 }}>{t}</div>
      ))}
    </div>
  )
  return (
    <div style={{ fontFamily: T.font.sans, margin: '2rem 0', padding: 24, background: T.surface.canvas, borderRadius: 12, border: `1px solid ${T.surface.border}` }}>
      <div style={{ display: 'flex', gap: 16, alignItems: 'stretch' }}>
        {col(T.problem, 'Before — 거대 Aggregate', before)}
        <div style={{ display: 'flex', alignItems: 'center', color: T.ink.muted, fontSize: 22 }}>→</div>
        {col(T.solution, 'After — 책임 분리', after)}
      </div>
    </div>
  )
}
```

(디자인 시스템 바인딩 시 소문자 헬퍼 이름 `col`/`card` 등은 `binding.json` 어휘의
camelCase를 따른다. 대문자 태그가 아니라 함수 호출이라 어느 MDX 호스트에서도 안전하다.)

## 안 하는 것
- Mermaid·React Flow·Recharts 등 라이브러리 도입, 실데이터 바인딩, 인터랙션 → 정적
  개념도만 만든다.
- 프로젝트 컴포넌트 import / repo에 theme 파일 생성(사용자가 명시 요청하지 않는 한).
- PPT/PDF 등 3차 산출물 변환.
- 대화 로그(`transcript.jsonl`)를 트리로 그리기 → `conversation-graph-mdx` 스킬.
