<!-- BOOTSTRAP:WIRING START — project-bootstrapper가 생성/관리하는 섹션 -->
# {프로젝트명} — 에이전트 운영 가이드

이 프로젝트는 `project-bootstrapper`로 부트스트랩되었다. 작업하는 에이전트는 아래 배선을 따른다.

## 산출물 지도

- **거버넌스 문서** (`<관리폴더>/`): `PLAN.md`(운영 방식 결정 기록·인터랙티브 소통 창구), `WORKFLOW.md`(작업 흐름), `BACKLOG.md`/`WBS.md`(작업 추적).
- **문서 기반 지시 창구** (`<project-root>/ORDER.md`): 인터랙티브 대화 대신 문서로 들어오는 상시 지시. `process-order` 스킬이 처리·봉인한다.
- **claude 도구** (`.claude/`): phase별 스킬(`.claude/skills/<phase>/`), 지시 처리 스킬(`.claude/skills/process-order/`), 본 `CLAUDE.md`.

## 작업 배선

1. **phase 작업 전**: `<관리폴더>/WORKFLOW.md`의 해당 "Phase" 섹션(목적·입력·절차·DoD)을 먼저 읽는다.
2. **절차 수행**: 해당 phase에 연결된 스킬(`.claude/skills/<phase>/`)이 있으면 그 스킬을 호출해 절차를 따른다.
3. **작업 후**: `<관리폴더>/BACKLOG.md`(또는 `WBS.md`)에서 관련 항목 상태를 갱신한다(`done` 등).
4. **새 산출물**: 에이전트가 반복 참고할 산출물이 필요하면 임의 파일이 아니라 claude-native 도구를 우선 만든다 — 반복 절차는 **skill**, 항상 참고할 지식은 **CLAUDE.md/참고문서**, 자동화는 **hook/command** 로 만들어 `.claude/`에 둔다.

## 문서 기반 지시(ORDER.md) 배선

- 사용자는 인터랙티브 대화 대신 `<project-root>/ORDER.md`의 `## 신규 지시` 영역에 지시를 적을 수 있다.
- 신규 지시가 있으면 **`process-order` 스킬을 호출**해 수행하고, 완료된 지시를 `## 처리 완료 (COMMITTED)` 영역에 **편집 금지 봉인 블록**으로 옮긴다.
- 봉인된 블록(`<!-- ORDER:COMMITTED ... -->` 쌍 사이)은 **수정·삭제하지 않는다.** 지시 철회·정정은 이전 내용을 고치는 게 아니라 `## 신규 지시`에 새 revert 지시(`reverts=ORD-NNN`)를 추가해 되돌린다(git revert 의미론).

## 규칙·컨벤션

{PLAN.md의 "규칙·컨벤션·협업 톤" 섹션 내용}
<!-- BOOTSTRAP:WIRING END -->
