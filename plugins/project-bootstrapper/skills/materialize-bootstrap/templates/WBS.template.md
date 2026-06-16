---
type: wbs
project: {프로젝트명}
updated: {YYYY-MM-DD}
source: ./PLAN.md
---

# WBS — {프로젝트명}

> Work Breakdown Structure. 작업을 계층적으로 분해해 추적한다.
> 상태 값: `todo` | `in-progress` | `blocked` | `done`

| WBS 코드 | 작업 | 담당 | 산정(예: 2d) | 상태 | 선행(코드) |
|---|---|---|---|---|---|
| 1 | {대분류} | | | todo | — |
| 1.1 | {세부 작업} | | | todo | — |
| 1.2 | {세부 작업} | | | todo | 1.1 |
| 2 | {대분류} | | | todo | 1 |

## 규칙

- 코드는 점 표기 계층(`1`, `1.1`, `1.1.1`)으로 부여한다.
- 상위 작업의 상태는 하위 작업이 모두 `done`일 때 `done`으로 바꾼다.
- 선행 작업이 있으면 "선행" 칸에 해당 코드를 적는다.
