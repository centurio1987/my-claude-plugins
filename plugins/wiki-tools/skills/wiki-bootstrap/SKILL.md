---
name: wiki-bootstrap
description: >
  새로운 LLM-driven 위키 프로젝트를 초기화할 때 사용하는 스킬.
  사용자가 "새 위키 만들어줘", "위키 프로젝트 초기화해줘", "wiki bootstrap", "wiki init",
  "새 지식 베이스 시작하고 싶어", "wiki 구조 잡아줘", "start a new wiki", "initialize wiki",
  "개인 위키 만들어줘", "지식 베이스 초기화" 같은 표현을 사용할 때 반드시 이 스킬을 사용한다.
  현재 작업 디렉토리에 CLAUDE.md나 wiki/ 디렉토리가 없는 경우에도 트리거한다.
---

# Wiki Bootstrap

Karpathy의 wiki-llm 패턴에 기반한 LLM-driven 개인 지식 베이스를 처음부터 설정한다.

**핵심 원칙 (Karpathy wiki-llm):**
- 인간은 소스를 큐레이션하고 질문을 던진다
- LLM은 요약·상호 참조·파일링·일관성 유지를 담당한다
- 위키는 시간이 지날수록 누적되고 풍부해지는 영구 산출물이다
- 매번 처음부터 다시 만들지 않는다

## Phase 1 — 인터뷰

다음 5개 질문을 **한 메시지에 묶어** 사용자에게 묻는다. 이미 답이 나온 것은 건너뛴다.

1. 이 위키에 어떤 종류의 지식을 모을 예정인가? (예: 기술/독서/연구/업무/개인 메모)
2. 위키를 저장할 디렉토리 경로는? (기본값: 현재 작업 디렉토리)
3. 주요 언어는? (한국어 / 영어 / 혼합)
4. Obsidian과 연동해서 사용할 예정인가? (wikilink 렌더링 및 `.obsidian/` 설정 필요 여부)
5. 주로 사용할 raw 소스 유형은? (예: YouTube 링크, PDF, 웹 클리핑, Notion 내보내기, 마크다운 파일)

## Phase 2 — 디렉토리 구조 생성

인터뷰에서 받은 경로(없으면 현재 작업 디렉토리)에 다음 구조를 생성한다:

```
{wiki-root}/
├── CLAUDE.md            # LLM 운영 스키마
├── README.md            # 사용자용 안내
├── index.md             # 위키 카탈로그 (빈 템플릿)
├── log.md               # 활동 로그 (빈 템플릿)
├── raw/                 # 원본 소스 — LLM 수정 금지
│   └── assets/
└── wiki/
    ├── sources/         # 각 raw 소스의 요약 페이지
    ├── entities/        # 인물·조직·제품 등 고유 명사
    ├── concepts/        # 추상 개념·이론·용어
    └── syntheses/       # 비교·분석·종합
```

Obsidian 연동을 선택한 경우 `.obsidian/` 디렉토리도 생성한다.

## Phase 3 — CLAUDE.md 생성

인터뷰 답변에 맞춰 맞춤 CLAUDE.md를 작성한다. 반드시 아래 9개 섹션을 포함한다:

**1. 핵심 원칙** — LLM의 역할(잡일 전담), 위키의 누적 속성

**2. 디렉토리 구조** — Phase 2에서 생성한 구조를 문서화. raw/는 불변·읽기 전용 명시

**3. 페이지 작성 규칙**
- 언어: 인터뷰 답변에 따라 한국어/영어/혼합 명시
- YAML frontmatter 필수 필드: `type`, `created`, `updated`, `tags`, `sources`
- 내부 참조: Obsidian wikilink `[[페이지 이름]]`
- 외부 URL: 일반 마크다운 링크
- 페이지 끝 `## 출처` 섹션 필수
- 카테고리별 페이지 구조 (sources/entities/concepts/syntheses 각각의 필수 섹션)

**4. 운영(Operations)**
- Ingest: 읽기 → 사용자와 핵심 takeaway 논의(1~2턴) → 요약 페이지 → 횡단 갱신 → index/log 업데이트 → 보고
- Query: index.md 먼저 읽기 → 관련 페이지 식별 → 출처 명시 → syntheses 저장 제안
- Lint: 모순·stale·orphan·missing·gap 점검

**5. index.md 형식** — 카테고리별 섹션, 한 줄 요약 형식

**6. log.md 형식** — append-only, `## [YYYY-MM-DD] {kind} | {제목}` prefix, 2~5줄 본문

**7. 모순·불확실성 표기 규약**
- `> ⚠️ 모순: ...`
- `> ❓ 불확실: ...`
- `> 🕰️ 시점 의존: ...`

**8. 협업 톤** — 인터뷰 언어 설정에 맞춤

**9. Anti-patterns** — raw/ 수정 금지, 출처 없는 단언 금지, 모순 덮기 금지, index 미갱신 금지

raw 소스 유형에 따라 Ingest 절차에 소스별 안내(PDF 처리, YouTube 링크 처리 등)를 추가한다.

## Phase 4 — 템플릿 파일 생성

**index.md:**
```markdown
---
type: index
updated: {오늘 날짜}
---

# Wiki Index

## Sources

## Entities

## Concepts

## Syntheses
```

**log.md:**
```markdown
---
type: log
updated: {오늘 날짜}
---

# Activity Log

## [{오늘 날짜}] meta | Wiki 초기화
- wiki-bootstrap 스킬로 프로젝트 구조 생성
- CLAUDE.md, index.md, log.md, README.md 생성
- raw/, wiki/ 디렉토리 구조 생성
```

**README.md:**
```markdown
# {위키 이름}

LLM-driven 개인 지식 베이스.

## 시작하기

1. `raw/` 폴더에 소스 파일을 추가한다 (PDF, 마크다운, 링크 등)
2. Claude에게 "ingest해줘" 또는 "이거 정리해줘"라고 말한다
3. 질문이 있으면 Claude에게 직접 묻는다 — 위키에서 찾아서 답해준다

## 디렉토리 구조

- `raw/` — 원본 소스 (변경하지 말 것)
- `wiki/` — Claude가 관리하는 페이지들
- `index.md` — 전체 페이지 카탈로그
- `log.md` — 활동 기록

## 운영 규칙

`CLAUDE.md` 참고.
```

## Phase 5 — 완료 보고

생성된 파일 목록을 보여주고 다음을 안내한다:
- "raw/ 폴더에 소스를 넣고 'ingest해줘'라고 말하면 위키가 채워집니다"
- Obsidian 연동 선택 시: "이 폴더를 Obsidian vault로 열면 됩니다"
- CLAUDE.md를 Claude Code에 로드하면 운영 규칙이 적용됨을 안내
