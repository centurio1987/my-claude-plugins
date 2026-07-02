---
name: wiki-forge
description: >
  위키를 새로 만들거나 지식 관리 환경을 구축하려는 요청의 기본 진입점(front door).
  인터뷰로 위키의 목적을 규명한 뒤 LLM-driven 위키(Karpathy wiki-llm 패턴)를 스캐폴딩하고
  graphify 지식그래프·시각화 레이어까지 한 번에 연결하는 풀 셋업 오케스트레이터.
  사용자가 "위키 만들어줘", "위키 프로젝트 만들어줘", "새 위키 만들어줘", "개인 위키 만들어줘",
  "wiki 만들어줘", "지식을 위키로 정리/관리하는 프로젝트(환경) 만들어줘", "지식 베이스 구축해줘",
  "knowledge base/wiki 만들어줘", "build a wiki", "create a wiki", "start a new wiki",
  "llm 위키 셋업", "graphify로 지식그래프 위키 만들어줘", "wiki forge", "위키 환경 벼려줘",
  "지식베이스 처음부터 구축해줘", "지식그래프까지 되는 위키 만들어줘" 같이 말하거나,
  현재 작업 디렉토리에 CLAUDE.md·wiki/ 가 없는 상태에서 위키/지식베이스 생성을 요청할 때 이 스킬을 사용한다.
  실제 디렉토리 뼈대 생성은 내부에서 wiki-bootstrap 에 위임하므로, 위키 생성 요청은 초기화만
  원한다고 명시하지 않는 한 기본적으로 이 스킬로 처리한다.
  인터뷰·graphify 없이 순수 뼈대만 원하면 wiki-bootstrap, 기존 위키 검증은 wiki-validate,
  재구성은 wiki-restructure를 쓴다.
  이 스킬은 (1) 목적 규명 인터뷰 + (2) 위키 스캐폴딩 + (3) graphify 그래프 레이어를 붙이는 풀 셋업이다.
  의존성(brainstorming·graphify)이 없으면 막지 않고 설치를 주도하며, 그래도 없으면 내장 인터뷰·graphify 생략으로 폴백해 위키 생성을 완주한다.
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

### 0-1. brainstorming(Superpowers) — 없으면 설치 주도, 그래도 없으면 내장 인터뷰로 폴백
사용 가능한 스킬 목록에 `brainstorming`이 있는지 확인한다. **있으면** Phase 1에서 인터뷰를 위임한다.

**없어도 여기서 중단하지 않는다.** 다음 순서로 처리한다:

1. **설치 제안.** brainstorming은 Superpowers 플러그인 소속이라 플러그인 설치·세션 재시작이 필요하고, 이는 슬래시 명령이라 에이전트가 직접 실행할 수 없다. 사용자가 지금 설치를 원하면 아래를 안내한다(설치 후 재시작하면 더 풍부한 인터뷰가 가능):
   ```
   1) /plugin marketplace add obra/superpowers
   2) superpowers 플러그인 설치
   3) 세션 재시작 후 다시 "위키 환경 만들어줘"
   ```
2. **폴백(기본).** 사용자가 설치를 원치 않거나 지금 재시작이 곤란하면, wiki-forge가 **Phase 1 인터뷰를 직접 진행**한다(질문 세트는 Phase 1에 그대로 있다). brainstorming 부재가 위키 생성을 막지 않는다.

### 0-2. graphify CLI — 없으면 설치 주도, 실패/거부 시 옵션으로 강등
1. `command -v graphify`로 확인. 실패하면 `~/.local/bin/graphify`, `$(uv tool dir 2>/dev/null)` 하위, `~/.cargo/bin`까지 탐색한다.
2. 그래도 없으면 **중단하지 않는다.** 설치를 제안하고, 사용자가 승인하면 직접 실행한다(uv tool 설치는 Bash로 실행 가능):
   ```
   uv tool install graphifyy   # PyPI 패키지명은 graphifyy(y 두 개), CLI는 graphify
   uv tool update-shell        # PATH 문제 시. 이후 새 셸/재확인
   ```
   - PATH 갱신이 필요해 같은 세션에서 즉시 인식되지 않으면, 사용자가 `! ` 프리픽스로 재확인하도록 안내한다. (Claude Code 스킬 등록 `graphify claude install`은 위키 루트에서 Phase 3에 실행한다.)
   - **설치가 실패하거나 사용자가 원치 않으면 graphify를 옵션으로 강등한다:** Phase 2까지만 진행해 위키를 완성하고 **Phase 3(그래프 레이어)는 건너뛴다.** CLAUDE.md·README·완료 보고에 "나중에 graphify 설치 후 `graphify claude install`로 그래프 레이어를 배선할 수 있다"를 남긴다. graphify 부재가 위키 생성을 막지 않는다.
3. (설치된 경우) **버전·명령 표면을 대조**한다: `graphify --version`과 `graphify --help`(및 하위 명령 `--help`)로, 이 스킬이 쓰는 명령(`graphify claude install`, `graphify .`, `--update`, `--cluster-only`, `query`/`path`/`explain`)이 실제 지원되는지 확인한다. **미지원 옵션은 지원되는 대체 명령으로 폴백**하고, 본문의 안내 문구도 그에 맞춘다.

### 0-3. 대상 경로 경계 확인
위키 루트 후보(기본: 현재 작업 디렉토리, 또는 인터뷰에서 받을 경로)에 이미 `CLAUDE.md`·`wiki/`·`graphify-out/`이 있으면 "기존 위키 감지"로 알린다. **덮어쓰지 않는다** — 이어붙이기(멱등 갱신)인지 새 경로로 만들 것인지 사용자에게 확인하고 진행한다.

### 0-4. 프라이버시 고지
graphify는 LLM 기반 추출로 콘텐츠를 처리한다. 민감 자료를 넣기 전에 처리 방식(외부 전송 여부/로컬 처리)과 제외 경로를 사용자에게 고지한다(근거는 `references/graphify-integration.md`). 비밀·개인 파일은 `raw/` 밖에 두거나 제외 패턴으로 관리하도록 안내한다.

**0-1·0-2는 더 이상 진행을 막지 않는다** — 설치 여부에 따라 위임/폴백(0-1)·필수/옵션(0-2)이 갈릴 뿐이다. **0-3(기존 위키 경계 처리 확정)과 0-4(프라이버시 고지)를 마치면 Phase 1로.**

---

## Phase 1 — 목적 규명 인터뷰 (brainstorming 위임, 없으면 직접)

brainstorming이 있으면 **그 스킬을 호출**해 한 질문씩 인터뷰를 진행한다. **0-1 폴백으로 brainstorming이 없으면 wiki-forge가 아래 항목을 직접 한 질문씩 물어** 인터뷰를 진행한다(핸드오프 없이 답변만 수집). 어느 경로든 규명 목표는 동일하다:

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

## Phase 3 — graphify 그래프 레이어 배선 (graphify 있을 때만, 멱등)

> **0-2에서 graphify를 옵션으로 강등했으면 이 Phase 전체를 건너뛴다.** 위키는 Phase 2에서 이미 완성돼 있으므로, Phase 4에서 "graphify 미설치로 그래프 레이어 생략됨 — 나중에 배선 가능"만 보고한다.

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

- **단계별 체크포인트:** Phase 0~3 각각의 결과를 요약한다. brainstorming 폴백(내장 인터뷰 사용) 여부와 graphify 강등(Phase 3 생략) 여부를 명시하고, 강등했다면 "나중에 graphify 설치 후 `graphify claude install`로 배선"이라는 재개 경로를 알린다. 실패·생략한 단계가 있으면 어디서 왜 그랬는지·재실행 방법을 명확히 보고한다(반쯤 구성된 상태를 숨기지 않는다).
- 생성/수정된 파일 목록.
- **다음 단계 순서:** `raw/`에 첫 소스 추가 → "ingest해줘" → `graphify .`로 최초 그래프 빌드 → `graphify-out/graph.html` 열기.
- 조회 워크플로우: 의미 질의는 `graphify query`, 정확 검색은 grep.
- Obsidian 연동을 선택했으면 이 폴더를 vault로 여는 법 안내.
