---
type: workflow
project: {프로젝트명}
updated: {YYYY-MM-DD}
source: ./PLAN.md
---

# WORKFLOW — {프로젝트명}

> 이 프로젝트의 작업 흐름 정의. `PLAN.md`에서 생성·관리되며, 에이전트는 각 phase 작업 전에 해당 섹션을 참고한다.

## 개요

{전체 흐름 한 줄 요약}

## Phase 요약

| Phase | 목적 | 산출물 | 연결된 skill |
|---|---|---|---|
| {phase-id} | {목적} | {산출물} | {`.claude/skills/<phase>/` 또는 —} |

---

## Phase: {phase-id}

- **목적**: {목적}
- **입력**: {입력}
- **절차**:
  1. {단계 1}
  2. {단계 2}
- **산출물**: {산출물}
- **완료 정의(DoD)**: {DoD}
- **연결된 skill**: {`.claude/skills/<phase>/SKILL.md` — 호출하여 절차 수행 / 없음}

<!-- phase마다 위 블록을 반복 -->
