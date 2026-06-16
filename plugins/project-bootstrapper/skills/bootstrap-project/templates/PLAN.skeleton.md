# PLAN — {프로젝트명}

> 이 파일은 프로젝트 부트스트랩의 **소통 창구**입니다. 유저가 직접 편집·갱신하는 유일한 파일이며,
> 여기서 합의된 내용으로 `WORKFLOW.md` / `BACKLOG.md` / `WBS.md`(관리폴더)와
> `.claude/` 도구(phase skill·CLAUDE.md)가 자동 생성됩니다.
> 비워둔 항목은 그대로 두셔도 됩니다 — 에이전트가 이어서 함께 구체화합니다.

- 상태: 초안 (작성 시작일: {YYYY-MM-DD})
- 관리폴더명: manage

---

## 1. 프로젝트 개요·목적

- 한 줄 요약:
- 해결하려는 문제 / 목표:
- 성공 기준(있다면):

## 2. 기술 스택·제약

- 언어/런타임:
- 주요 프레임워크·라이브러리:
- 인프라/배포:
- 제약 사항(성능·보안·규제·팀 규칙 등):

## 3. 산출물 정책 (claude-native 우선)

> 에이전트가 참고할 산출물은 임의 파일이 아니라 가능한 한 claude 도구로 만들어 `.claude/*`에 둡니다.
> 각 "필요"를 어떤 도구 유형으로 만들지 매핑하세요.

| 필요(무엇을 위해) | 도구 유형 | 위치 |
|---|---|---|
| (예: 반복되는 릴리스 절차) | skill | `.claude/skills/release/` |
| (예: 도메인 용어·아키텍처 지식) | CLAUDE.md / 참고문서 | `.claude/CLAUDE.md` |
| (예: 커밋 전 자동 검사) | hook / command | `.claude/` |

- 매핑 원칙: 반복 절차 → **skill**, 항상 참고할 지식 → **CLAUDE.md/참고문서**, 자동화 → **hook/command**.

## 4. 워크플로우

- 워크플로우 포함: (yes / no)
- 개요(전체 흐름 한 줄):

각 phase를 아래 형식으로 나열하세요. **절차가 구체적인 phase는 `skill화: yes`** 로 표시하면, 그 phase는 `.claude/skills/<phase>/`에 호출 가능한 스킬로 생성됩니다.

### Phase: {phase-id 예: design}
- 목적:
- 입력:
- 절차(단계):
  1.
  2.
- 산출물:
- 완료 정의(DoD):
- skill화: (yes / no)

<!-- 필요한 만큼 Phase 블록을 복제하세요 -->

## 5. 백로그 / WBS

- 포함 여부: (backlog / wbs / 둘 다 / 없음)
- 초기 항목(아는 만큼):
  -
  -

## 6. 관리폴더·파일 배치

- 관리폴더명(기본 `manage`):
- 거버넌스 문서 배치: `<관리폴더>/PLAN.md`, `WORKFLOW.md`, `BACKLOG.md`, `WBS.md`
- claude 도구 배치: `.claude/CLAUDE.md`, `.claude/skills/<phase>/`
- 문서 기반 지시 창구: `<project-root>/ORDER.md` + `.claude/skills/process-order/` (항상 자동 생성 — 설계 불필요)

## 7. 규칙·컨벤션·협업 톤

- 코딩/문서 컨벤션:
- 브랜치·커밋 규칙:
- 에이전트 협업 톤(언어·존댓말 여부 등):
- 기타 지켜야 할 규칙:
