---
name: wiki-forge
description: >
  인터뷰로 위키의 목적을 규명한 뒤 LLM-driven 위키(Karpathy wiki-llm 패턴)를 스캐폴딩하고
  graphify 지식그래프·시각화 레이어까지 한 번에 연결하는 풀 셋업 오케스트레이터.
  사용자가 "지식을 위키로 관리하는 환경 만들어줘", "llm 위키 셋업", "graphify로 지식그래프 위키 만들어줘",
  "wiki forge", "위키 환경 벼려줘", "지식베이스 처음부터 구축해줘", "knowledge wiki 환경 구축",
  "지식그래프까지 되는 위키 만들어줘" 같이 말할 때 이 스킬을 사용한다.
  단순 초기화만 원하면 wiki-bootstrap, 기존 위키 검증은 wiki-validate, 재구성은 wiki-restructure를 쓴다.
  이 스킬은 (1) 목적 규명 인터뷰 + (2) 위키 스캐폴딩 + (3) graphify 그래프 레이어를 모두 붙이는 풀 셋업일 때 쓴다.
---

# Wiki Forge

지식을 위키로 관리하는 환경을 **한 번에 벼려낸다(forge)**. 세 가지를 결합한 오케스트레이터다:

- **LLM Wiki (Karpathy wiki-llm 패턴)** — 매번 재생성하는 RAG가 아니라, LLM이 소유·유지하는 **누적 마크다운 위키**. 인간은 소스를 큐레이션·질문하고, LLM은 요약·상호참조·일관성 유지를 맡는다.
- **wiki-bootstrap 스킬** — 실제 디렉토리/CLAUDE.md 스캐폴딩을 담당(재사용, 재작성하지 않음).
- **graphify** (`github.com/safishamsi/graphify`, MIT) — 위키 폴더를 쿼리 가능한 지식 그래프로 바꾸고 `graph.html` 인터랙티브 시각화를 만드는 오픈소스 Claude Code 스킬/CLI.

핵심은 **위키의 목적을 먼저 분명히** 하는 것이다 — 목적을 규명한 인터뷰 결과가 카테고리·엔티티 유형·링크 규칙·graphify 질의 설계에 반영된다.

> graphify 설치·명령·CLAUDE.md 삽입 스니펫·트러블슈팅은 `references/graphify-integration.md`를 참조한다. Phase 0·Phase 3을 수행하기 전에 반드시 읽는다.

---

## Phase 0 — 의존성 프리플라이트 & 경계 확인 (게이트)

**여기서 막히면 진행하지 않는다. 각 항목을 순서대로 확인한다.**

### 0-1. brainstorming(Superpowers) 가용성
사용 가능한 스킬 목록에 `brainstorming`이 있는지 확인한다. 없으면 **여기서 중단**하고 안내한다:

```
brainstorming(Superpowers) 스킬이 설치돼 있지 않습니다. wiki-forge는 목적 규명 인터뷰에 이 스킬을 사용합니다.
설치 후 다시 실행해 주세요:
  1) /plugin marketplace add obra/superpowers
  2) superpowers 플러그인 설치
  3) 세션 재시작 후 다시 "위키 환경 만들어줘"
```

### 0-2. graphify CLI 확인 (PATH 회피 포함)
1. `command -v graphify`로 확인. 실패하면 `~/.local/bin/graphify`, `$(uv tool dir 2>/dev/null)` 하위, `~/.cargo/bin`까지 탐색한다.
2. 그래도 없으면 설치를 안내한다. 설치·인증 명령은 사용자가 직접 실행하도록 `! ` 프리픽스 사용을 제안한다:
   ```
   uv tool install graphifyy   # PyPI 패키지명은 graphifyy(y 두 개), CLI는 graphify
   graphify install            # Claude Code 스킬 등록
   uv tool update-shell        # PATH 문제 시. 이후 새 셸/재확인
   ```
3. 설치 확인 후 **버전·명령 표면을 대조**한다: `graphify --version`과 `graphify --help`(및 하위 명령 `--help`)로, 이 스킬이 쓰는 명령(`graphify claude install`, `graphify .`, `--update`, `--cluster-only`, `query`/`path`/`explain`)이 실제 지원되는지 확인한다. **미지원 옵션은 지원되는 대체 명령으로 폴백**하고, 본문의 안내 문구도 그에 맞춘다.

### 0-3. 대상 경로 경계 확인
위키 루트 후보(기본: 현재 작업 디렉토리, 또는 인터뷰에서 받을 경로)에 이미 `CLAUDE.md`·`wiki/`·`graphify-out/`이 있으면 "기존 위키 감지"로 알린다. **덮어쓰지 않는다** — 이어붙이기(멱등 갱신)인지 새 경로로 만들 것인지 사용자에게 확인하고 진행한다.

### 0-4. 프라이버시 고지
graphify는 LLM 기반 추출로 콘텐츠를 처리한다. 민감 자료를 넣기 전에 처리 방식(외부 전송 여부/로컬 처리)과 제외 경로를 사용자에게 고지한다(근거는 `references/graphify-integration.md`). 비밀·개인 파일은 `raw/` 밖에 두거나 제외 패턴으로 관리하도록 안내한다.

**0-1 ~ 0-4를 모두 통과하면 Phase 1로.**

---

## Phase 1 — 목적 규명 인터뷰 (brainstorming 위임)

**brainstorming 스킬을 호출**해 한 질문씩 인터뷰를 진행한다. brainstorming에게 다음을 규명 목표로 명시해서 넘긴다:

- 위키의 **목적·도메인** (무엇을 위한 지식 베이스인가)
- 수집할 지식 종류 (기술/독서/연구/업무/개인 등)
- 주요 raw 소스 유형 (PDF / YouTube 링크 / 웹 클리핑 / Notion 내보내기 / 마크다운 노트)
- 주 언어 (한국어 / 영어 / 혼합)
- 예상 **질의 패턴** (앞으로 이 위키에 무엇을 자주 물을 것인가)
- Obsidian 연동 여부
- 저장 경로 (기본: 현재 작업 디렉토리)

### 인터뷰 → 구조 매핑 (중요)
수집한 목적·질의 패턴을 **저장 경로 결정에만 쓰지 말고** Phase 2의 CLAUDE.md 커스터마이즈 입력으로 구조화한다. 인터뷰가 끝나면 다음을 도출해 Phase 2에 넘길 수 있게 정리한다:

- 도메인에 맞는 **카테고리** (sources/entities/concepts/syntheses 하위 분류)
- 이 도메인에서 다룰 **엔티티 유형 목록** (예: 인물·논문·라이브러리·회사 등)
- **내부 링크 규칙** (무엇을 어떤 페이지로 링크할지)
- 질의 패턴에서 뽑은 **자주 쓸 graphify 질의 예시** 몇 개

### 제약 & 폴백 (중요)
brainstorming의 기본 종료 동작은 design 문서를 쓴 뒤 `writing-plans` 스킬로 핸드오프하는 것이다. wiki-forge는 brainstorming을 **인터뷰 도구로만** 쓴다:
- brainstorming에게 "요구사항 brief를 반환하는 데서 멈추고 구현 계획(writing-plans)으로 넘어가지 말 것"을 지시한다.
- **폴백:** 그럼에도 brainstorming이 다음 단계로 넘어가려 하면, 그 시점까지 수집된 답변만 취하고 이후 위임은 무시한 채 wiki-forge가 직접 Phase 2를 이어간다. (프롬프트 준수에만 의존하지 않는다.)

---

## Phase 2 — LLM-wiki 스캐폴딩 (wiki-bootstrap 재사용)

실제 디렉토리·파일 생성은 **`wiki-bootstrap` 스킬에 위임**한다. wiki-bootstrap 파일은 **수정하지 않는다.**

**위임 계약(확인됨):** `wiki-bootstrap`의 인터뷰는 "이미 답이 나온 것은 건너뛴다"고 명시돼 있다. 따라서:
1. wiki-bootstrap을 호출하기 직전에 Phase 1에서 확보한 5개 항목을 **명시적으로 요약해 컨텍스트에 제시**한다 — 지식 종류 / 저장 경로 / 언어 / Obsidian 연동 여부 / raw 소스 유형. 그러면 wiki-bootstrap이 자체 인터뷰를 자연히 스킵한다.
2. Phase 1의 인터뷰→구조 매핑 결과(도메인 카테고리·엔티티 유형·링크 규칙·graphify 질의 예시)도 함께 넘겨 CLAUDE.md 작성에 반영되게 한다.

**결과물** (`{wiki-root}/`):
```
CLAUDE.md   README.md   index.md   log.md
raw/  (+ raw/assets/)          # 불변·읽기 전용
wiki/{sources,entities,concepts,syntheses}/
```
(구조·CLAUDE.md 9개 섹션의 상세는 `../wiki-bootstrap/SKILL.md` Phase 2~4 참조.)

---

## Phase 3 — graphify 그래프 레이어 배선 (필수, 멱등)

**원칙: 모든 쓰기는 멱등하게.** 재실행 시 CLAUDE.md 섹션·log·`.gitignore`·훅이 중복되지 않도록 **마커 기반 삽입 / 존재 감지 후 갱신**을 적용한다. 명령 세부는 `references/graphify-integration.md` 참조.

1. **`graphify claude install`** — 위키 루트에 상시 지침 + PreToolUse 훅을 등록한다. 실행 **전에** `graphify claude install --help`로 어떤 파일/훅을 바꾸는지(기존 CLAUDE.md·사용자 훅 덮어쓰기 여부) 확인해 사용자에게 알린다. 이미 등록돼 있으면 재등록을 건너뛴다.

2. **초기 그래프 빌드는 최초 ingest 이후로 미룬다.** 스캐폴딩 직후 `raw/`가 비어 있어 `graphify .` 빌드가 실패하거나 무의미한 그래프만 만든다. 대신:
   - CLAUDE.md·README에 "첫 소스를 ingest한 뒤 `graphify .`로 최초 그래프를 만든다"를 명시한다.
   - CLAUDE.md의 ingest 워크플로우 안에 "ingest 후 `graphify . --update`로 그래프 갱신" 단계를 넣는다.
   - (옵션) Phase 4에서 사용자가 원하면 샘플 소스 1건을 ingest한 뒤 최초 빌드를 시연한다.

3. **CLAUDE.md에 graphify 운영 섹션 삽입** (마커로 감싼다). `references/graphify-integration.md`의 스니펫을 사용하며 다음을 담는다:
   - **조회 정책(완화):** 의미·관계 질의는 `graphify query "<질문>"` / `graphify path A B` / `graphify explain X`. **정확 문자열·파일 위치 검색은 grep/rg.** (graphify 전면 강제가 아니라 질의 성격에 따라 선택.)
   - **인덱싱 경계:** `graphify-out/`(생성물·재귀 입력 방지)와 비밀/제외 경로를 그래프 대상에서 제외. `raw/` 포함 여부는 도메인에 맞게 명시.
   - **시각화:** `graphify-out/graph.html`을 브라우저로 연다.

4. git 저장소면 `graphify-out/`을 `.gitignore`에 **중복 없이** 추가한다.

5. `log.md`에 `## [YYYY-MM-DD] meta | graphify 그래프 레이어 배선` 항목을 append한다(같은 항목 중복 방지).

---

## Phase 4 — 완료 보고 & 다음 단계

- **단계별 체크포인트:** Phase 0~3 각각의 성공 여부를 요약한다. 실패한 단계가 있으면 어디서 왜 막혔는지·재실행 방법을 명확히 보고한다(반쯤 구성된 상태를 숨기지 않는다).
- 생성/수정된 파일 목록.
- **다음 단계 순서:** `raw/`에 첫 소스 추가 → "ingest해줘" → `graphify .`로 최초 그래프 빌드 → `graphify-out/graph.html` 열기.
- 조회 워크플로우: 의미 질의는 `graphify query`, 정확 검색은 grep.
- Obsidian 연동을 선택했으면 이 폴더를 vault로 여는 법 안내.
