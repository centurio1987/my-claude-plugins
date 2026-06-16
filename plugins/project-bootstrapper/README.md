# project-bootstrapper

새 프로젝트를 부트스트랩한다 — 그 프로젝트에서 작업할 에이전트가 **스스로 참고할 산출물**(워크플로우·백로그/WBS·phase별 절차)을 일관된 형태로 갖추도록 초기 운영 환경을 설정한다.

## 설계 원칙

- **PLAN.md 단일 소통 창구**: 부트스트랩(운영 방식 정의) 단계에서 유저가 직접 편집·갱신하는 파일은 `<관리폴더>/PLAN.md` 하나뿐. 나머지 산출물은 모두 PLAN.md에 근거해 에이전트가 생성·관리한다.
- **claude-native 우선**: 에이전트가 참고할 산출물은 가능한 한 claude 도구(skill·command·agent·`CLAUDE.md`)로 만들어 `.claude/*`에 둔다. 거버넌스 문서는 사람이 찾기 쉬운 최상위 관리폴더(기본 `manage/`)에 둔다.
- **두 개의 창구**: `PLAN.md`는 *운영 방식을 정의하는 1회성 인터랙티브 창구*, `<project-root>/ORDER.md`는 *운영 중 문서로 지시를 받는 상시 창구*다. ORDER.md의 완료 지시는 편집 금지 구획으로 봉인되며, 철회는 수정이 아니라 새 revert 지시로 한다(git revert 의미론).

## 두 개의 스킬

| 스킬 | 역할 |
|---|---|
| `bootstrap-project` | 오케스트레이터. `manage/PLAN.md` 스켈레톤 제공 → 유저 초안 → 인터랙티브 리뷰·발전으로 운영 방식을 함께 정의한다. |
| `materialize-bootstrap` | 확정된 PLAN.md를 읽어 `manage/`의 거버넌스 문서와 `.claude/`의 phase skill·`CLAUDE.md`를 생성한다. 재실행 가능. |

## 사용법

```
/project-bootstrapper:bootstrap-project
```

1. **스켈레톤**: `manage/PLAN.md`(항목 위주)가 생성된다.
2. **초안**: 유저가 PLAN.md 섹션을 직접 채운 뒤 메시지로 알린다.
3. **발전**: 에이전트가 섹션별 질문으로 PLAN.md를 함께 구체화한다.
4. **확정·생성**: PLAN.md 확정 시 `materialize-bootstrap`이 산출물을 생성한다(직접 실행도 가능).

## 생성되는 레이아웃

```
<project-root>/
├── manage/                  # 폴더명은 PLAN.md에서 변경 가능 (default: manage)
│   ├── PLAN.md              # 인터랙티브 소통 창구 + 결정 기록
│   ├── WORKFLOW.md          # workflow 포함 시
│   ├── BACKLOG.md           # backlog 선택 시
│   └── WBS.md               # wbs 선택 시
├── ORDER.md                 # 문서 기반 상시 지시 창구 (항상 생성, append-only 봉인 원장)
└── .claude/
    ├── CLAUDE.md            # 배선: manage/* 참고 + phase skill 호출 + ORDER.md 처리 + 도구 우선 원칙
    └── skills/
        ├── <phase>/SKILL.md      # 구체적 절차가 있는 각 phase
        └── process-order/SKILL.md  # ORDER.md 지시 수행·봉인 (항상 생성)
```

## ORDER.md — 문서 기반 지시 창구

인터랙티브 대화 대신 문서로 지시하고 싶을 때 `<project-root>/ORDER.md`의 `## 신규 지시` 영역에 지시를 적는다. `process-order` 스킬이 처리한다:

1. 신규 지시를 수행한다(수행 직전 `status=processing`으로 표시 → 세션 중단 시 중복 수행 방지).
2. 완료된 지시는 `## 처리 완료 (COMMITTED)` 영역에 `<!-- ORDER:COMMITTED ... -->` 주석 쌍으로 **봉인**(편집 금지)한다.
3. 지시 철회·정정은 봉인 블록을 고치는 게 아니라 `## 신규 지시`에 새 revert 지시(`reverts=ORD-NNN`)를 추가한다. 이력은 불변이며 되돌림도 새 항목으로 남는다.

## 재실행

PLAN.md를 수정한 뒤 `materialize-bootstrap`을 다시 실행하면 산출물이 갱신된다(덮어쓰기 전 확인). 생성된 phase skill은 YAML 프론트매터 셀프 린팅으로 정합성을 검증한다.
