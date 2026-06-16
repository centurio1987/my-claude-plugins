---
name: materialize-bootstrap
description: >
  확정된 PLAN.md를 바탕으로 프로젝트 부트스트랩 산출물을 실제로 생성하는 스킬.
  사용자가 "PLAN.md 반영해줘", "산출물 생성해줘", "워크플로우/백로그/WBS 만들어줘",
  "부트스트랩 머티리얼라이즈", "materialize bootstrap", "이제 .claude 도구 만들어줘",
  "PLAN대로 셋업 적용해줘" 같이 말하거나 bootstrap-project가 인계할 때 사용한다.
  manage/PLAN.md를 읽어 manage/의 WORKFLOW.md·BACKLOG.md·WBS.md와 .claude/의 phase skill,
  .claude/CLAUDE.md(배선), 그리고 프로젝트 루트의 ORDER.md(문서 기반 지시 창구)와
  .claude/skills/process-order(지시 처리 스킬)를 생성한다. 재실행 가능(idempotent)하며 덮어쓰기 전 확인한다.
metadata:
  version: "0.1.0"
---

# Materialize Bootstrap (머티리얼라이저)

확정된 `<관리폴더>/PLAN.md`를 읽어 산출물을 생성한다. **재실행 가능**해야 하며, 기존 파일을 덮어쓰기 전에 유저에게 확인한다.

## Phase 0 — PLAN 로드 & 검증

1. `<관리폴더>/PLAN.md`를 읽는다(관리폴더명은 PLAN.md의 "관리폴더명" 항목, 기본 `manage`). 없으면 `bootstrap-project`를 먼저 실행하라고 안내하고 종료한다.
2. PLAN의 핵심 섹션이 채워졌는지 점검한다. 비어 있으면 어떤 섹션이 비었는지 보고하고, 계속할지 확인한다.
3. 생성 대상 목록을 한 번에 요약해 유저에게 보여준다(어떤 파일이 새로 생기고 어떤 파일이 덮어써질지). PLAN 선택과 무관하게 **항상** 생성되는 항목은 `<project-root>/ORDER.md`(없을 때만)와 `.claude/skills/process-order/SKILL.md`다.

## Phase 1 — manage/ 거버넌스 문서

PLAN의 선택에 따라 생성한다. 각 템플릿은 `templates/`의 상대경로로 읽는다.

- **워크플로우 포함 시** → `templates/WORKFLOW.template.md`로 `<관리폴더>/WORKFLOW.md` 생성.
  - PLAN의 Phase 블록들을 phase 요약 표 + phase별 상세 섹션으로 채운다.
  - 각 phase의 `skill화` 값과, 생성될 스킬 경로(`.claude/skills/<phase>/`)를 "연결된 skill" 칸에 기록한다.
- **백로그 선택 시** → `templates/BACKLOG.template.md`로 `<관리폴더>/BACKLOG.md` 생성. PLAN의 초기 항목을 표에 채운다.
- **WBS 선택 시** → `templates/WBS.template.md`로 `<관리폴더>/WBS.md` 생성.

## Phase 2 — .claude/ phase skill 생성

PLAN에서 `skill화: yes`로 표시된 각 phase에 대해:

1. `templates/phase-skill.template.md`를 읽어 플레이스홀더를 PLAN의 해당 phase 내용으로 치환한다.
2. `.claude/skills/<phase-id>/SKILL.md`로 기록한다.
3. body는 입력·절차 step·출력을 담고, 상세 맥락은 `<관리폴더>/WORKFLOW.md`의 해당 phase 섹션을 참조하도록 한다.

## Phase 2.5 — ORDER.md & process-order 스킬 (문서 기반 지시 창구)

PLAN 선택과 무관하게 **항상** 생성한다(이 플러그인의 기본 산출물). 인터랙티브 창구 PLAN.md와 별개로, 운영 중 문서로 지시를 받는 창구다.

1. `templates/ORDER.template.md`로 **`<project-root>/ORDER.md`**(관리폴더가 아니라 프로젝트 루트)를 생성한다.
   - **이미 존재하면 덮어쓰지 않는다.** ORDER.md는 봉인 이력을 누적하는 append-only 원장이므로 보존한다(재실행 시에도).
2. `templates/process-order-skill.template.md`로 `.claude/skills/process-order/SKILL.md`를 생성한다(플레이스홀더 `{프로젝트명}` 등을 치환). 이 스킬이 ORDER.md의 신규 지시를 수행·봉인하고 revert 의미론을 관리한다.

## Phase 3 — .claude/CLAUDE.md 배선

`templates/project-CLAUDE.template.md`로 `.claude/CLAUDE.md`를 생성/병합한다. 다음 배선 원칙을 명시한다:

1. phase 작업을 시작하기 전 `<관리폴더>/WORKFLOW.md`의 해당 phase 섹션을 먼저 참고한다.
2. 절차가 스킬화된 phase는 해당 phase skill을 호출한다.
3. 작업 후 `BACKLOG.md`/`WBS.md`의 상태를 갱신한다.
4. 새 산출물이 필요하면 임의 파일이 아니라 claude-native 도구(skill·command·agent·CLAUDE.md)를 우선 만들어 `.claude/`에 둔다.

기존 `.claude/CLAUDE.md`가 있으면 덮어쓰지 말고, 부트스트랩 배선 섹션만 추가/갱신한다.

## Phase 4 — 셀프 린팅

생성한 각 `.claude/skills/<phase>/SKILL.md`와 `.claude/skills/process-order/SKILL.md`에 대해 YAML 프론트매터를 검증한다:

```bash
python3 - "$f" <<'PY'
import sys, re
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
assert m, f"{p}: 프론트매터 없음"
fm = m.group(1)
try:
    import yaml            # 있으면 정식 YAML 파싱
    d = yaml.safe_load(fm)
    ok = bool(d and d.get("name") and d.get("description"))
except ModuleNotFoundError:  # 없으면 키 존재만 정규식으로 확인 (실패 처리하지 않음)
    ok = bool(re.search(r"^name:", fm, re.M) and re.search(r"^description:", fm, re.M))
assert ok, f"{p}: name/description 누락 또는 YAML 깨짐"
print(f"OK {p}")
PY
```

깨진 파일이 있으면 내용을 보고하고 재생성한다.

## Phase 5 — 완료 보고

생성된 파일 트리와 셀프 린팅 결과를 보여준 뒤 다음을 안내한다:
- "이 프로젝트에서 phase 작업을 시작하면 `.claude/CLAUDE.md`의 배선에 따라 WORKFLOW.md를 참고하고 phase 스킬을 호출하게 됩니다."
- PLAN.md를 수정한 뒤 이 스킬을 재실행하면 산출물이 갱신됨(덮어쓰기 전 확인).
