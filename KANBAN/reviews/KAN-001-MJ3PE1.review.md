---
card: KAN-001-MJ3PE1
title: authoring-kit 0.4.0 — 문체 설정 체계화(전역→voice 계승·어휘 가중치·정성 지시·편집기)
created: 2026-09-26
branch: KAN-001-MJ3PE1
worktree: /Users/centurio/orca/workspaces/my-claude-plugin/KAN-001-MJ3PE1-2
base: 12dc324
merged: 832d85e
status: 검토 대기
---

# KAN-001-MJ3PE1 검토 요청 — authoring-kit 0.4.0 — 문체 설정 체계화(전역→voice 계승·어휘 가중치·정성 지시·편집기)

카드: [KAN-001-MJ3PE1.md](../cards/KAN-001-MJ3PE1.md)

> 이 문서는 **검토를 위한 산출물**이다. 수행 내역은 카드 실행 문서에 있고, 착수 전
> 계획은 배치 문서에 있다. 여기 있는 것은 "지금 이 브랜치를 무엇으로 판정하는가" 뿐이다.

## 1. 검토 대상

| 항목 | 값 |
|---|---|
| 브랜치 | `KAN-001-MJ3PE1` — **머지됨**, 대상은 아래 고정 범위 |
| 워크트리 | `/Users/centurio/orca/workspaces/my-claude-plugin/KAN-001-MJ3PE1-2` |
| 베이스 | `12dc324` |
| 변경 훑기 | `git diff 12dc324..832d85e` |

**커밋 17건**

```text
832d85e Merge KAN-001-MJ3PE1: authoring-kit 0.4.0 문체 설정 체계화 (카드는 진행 중 유지)
aa5817a kanban: KAN-001-MJ3PE1 scope 기재 (plugins/authoring-kit/**, marketplace.json)
d1164ea kanban: KAN-001-MJ3PE1 S8 완료 (소급)
b26173b kanban: KAN-001-MJ3PE1 S7 완료 (소급)
ebd3d4e kanban: KAN-001-MJ3PE1 S6 완료 (소급)
f5ff3b4 kanban: KAN-001-MJ3PE1 S5 완료 (소급)
69fd4ae kanban: KAN-001-MJ3PE1 S4 완료 (소급)
027ab2b kanban: KAN-001-MJ3PE1 S3 완료 (소급)
4ffd70d kanban: KAN-001-MJ3PE1 S2 완료 (소급)
31733ac kanban: KAN-001-MJ3PE1 S1 완료 (소급)
3353d07 kanban: KAN-001-MJ3PE1 소급 기록 사실을 수행 내역에 남김
685f45b kanban: KAN-001-MJ3PE1 실행 문서 — 전략·실행 계획·검증 (소급)
5b28533 kanban: KAN-001-MJ3PE1 진행 중으로 이동
955ad1b kanban: KAN-001-MJ3PE1 할 일에 추가 (문체 설정 체계화, 소급)
c129205 Merge claude/beautiful-mccarthy-kxg2nl into KAN-001-MJ3PE1 — 소급: 먼저 수행한 작업을 카드 브랜치로
3dda6d1 kanban: 보드 환경 초기화 (layout 3)
3e1ada8 feat(authoring-kit) 0.4.0: 문체 설정 — 전역을 voice 가 계승하는 어휘 가중치·정성 지시와 편집기
```

**변경 파일 42개 (+7053 −101)**

| 파일 | 상태 | 추가 | 삭제 |
|---|:--:|---:|---:|
| `.claude-plugin/marketplace.json` | M | 2 | 2 |
| `.gitattributes` | M | 7 | 0 |
| `.gitignore` | M | 3 | 0 |
| `.kanban/archive.jsonl` | M | 0 | 0 |
| `.kanban/log.md` | M | 5 | 0 |
| `.kanban/reviews/.gitkeep` | M | 0 | 0 |
| `.kanban/state.json` | M | 63 | 0 |
| `KANBAN.board.html` | M | 1545 | 0 |
| `KANBAN.md` | M | 40 | 0 |
| `KANBAN/batches/.gitkeep` | M | 0 | 0 |
| `KANBAN/cards/KAN-001-MJ3PE1.md` | M | 58 | 0 |
| `KANBAN/reports/.gitkeep` | M | 0 | 0 |
| `KANBAN/requests/backlog/.gitkeep` | M | 0 | 0 |
| `KANBAN/requests/doing/.gitkeep` | M | 0 | 0 |
| `KANBAN/requests/done/.gitkeep` | M | 0 | 0 |
| `KANBAN/requests/review/.gitkeep` | M | 0 | 0 |
| `KANBAN/requests/todo/.gitkeep` | M | 0 | 0 |
| `KANBAN/reviews/.gitkeep` | M | 0 | 0 |
| `plugins/authoring-kit/.claude-plugin/plugin.json` | M | 5 | 3 |
| `plugins/authoring-kit/README.md` | M | 36 | 1 |
| `plugins/authoring-kit/fixtures/run_all.sh` | M | 1 | 0 |
| `plugins/authoring-kit/fixtures/test_plugin_shape.py` | M | 6 | 2 |
| `plugins/authoring-kit/fixtures/test_style.py` | M | 329 | 0 |
| `plugins/authoring-kit/scripts/authoring.py` | M | 54 | 3 |
| `plugins/authoring-kit/scripts/scan_ai_style.py` | M | 97 | 85 |
| `plugins/authoring-kit/scripts/scan_lexicon.py` | M | 107 | 0 |
| `plugins/authoring-kit/scripts/style_registry.py` | M | 845 | 0 |
| `plugins/authoring-kit/scripts/style_server.py` | M | 264 | 0 |
| `plugins/authoring-kit/skills/authoring-doctor/SKILL.md` | M | 11 | 0 |
| `plugins/authoring-kit/skills/authoring-gate/SKILL.md` | M | 16 | 1 |
| `plugins/authoring-kit/skills/authoring-method/SKILL.md` | M | 7 | 2 |
| `plugins/authoring-kit/skills/authoring-method/assets/QUALITY_RUBRIC.md` | M | 10 | 1 |
| `plugins/authoring-kit/skills/authoring-method/assets/style/lexicon.json` | M | 369 | 0 |
| `plugins/authoring-kit/skills/authoring-method/assets/style/qualitative.json` | M | 1056 | 0 |
| `plugins/authoring-kit/skills/authoring-style/SKILL.md` | M | 90 | 0 |
| `plugins/authoring-kit/skills/authoring-style/assets/STYLE_RESEARCH.md` | M | 147 | 0 |
| `plugins/authoring-kit/skills/authoring-style/assets/STYLE_SCHEMA.md` | M | 111 | 0 |
| `plugins/authoring-kit/skills/authoring-style/assets/research/lexicon-notes.md` | M | 588 | 0 |
| `plugins/authoring-kit/skills/authoring-style/assets/research/qualitative-notes.md` | M | 550 | 0 |
| `plugins/authoring-kit/skills/authoring-voice/SKILL.md` | M | 8 | 0 |
| `plugins/authoring-kit/skills/authoring-voice/assets/VOICE_SCHEMA.md` | M | 6 | 1 |
| `plugins/authoring-kit/ui/style-editor.html` | M | 617 | 0 |

**롤백 태그 0개** — 없음(`--tags` 를 넘기지 않았거나 아직 태그가 없습니다)

## 2. 검증 — 기준과 실행 결과

<!-- 기준은 카드 실행 문서 「검증」 절의 사본이다. 정본은 KANBAN/cards/KAN-001-MJ3PE1.md 이므로
     기준이 바뀌면 그쪽을 고치고 review-init --refresh 로 이 항만 다시 뜬다.
     결과는 착수한 쪽이 이미 돌린 것이다 — 검토자에게 다시 돌리라고 시키지 않는다.
     **다시 돌려 아래와 다르게 나오면 그 자체가 반려 사유다.** -->

**기준**

- `python3 plugins/authoring-kit/fixtures/test_style.py` → `통과 92 · 실패 0` (계승·검증·가중치 스캔·L0 항목 면제·resolve·lock·편집기 API)
- `test_scanner.py` · `test_linter.py` 통과, 대역 voice 로 돌린 `test_layer_separation.py` 32/32 (voice 간 누출 없음)
- `authoring.py style validate` → 정상
- 규칙 하나를 끈 돌연변이 실행에서 `test_style.py` 가 5건 실패 — 테스트가 실제로 잡는다
- Playwright 로 편집기 전체 흐름·라이트/다크·390px 폭 확인
- 알려진 실패(이 카드와 무관, 이전부터): `test_plugin_shape.py` 의 `authoring-write: 142줄 ≤ 130`

**실행 결과**

```text
$ test_style.py
문체 설정 통과.
통과 92 · 실패 0
$ test_scanner.py
통과 9 · 실패 0
$ test_linter.py
통과 25 · 실패 0
$ test_layer_separation.py
통과 32 · 실패 0
$ authoring.py style validate
문체 설정 정상 — 카탈로그 · 전역 · voice 전부
$ test_plugin_shape.py (기존 실패 — 12dc324 에서도 authoring-write SKILL.md 142줄)
  FAIL authoring-write: 142줄 ≤ 130 — 142줄
  - authoring-write: 142줄 ≤ 130 — 142줄
```

## 3. 판단 항목 — 스크립트가 판정할 수 없는 것

<!-- 스크립트가 판정할 수 없는 것만 적는다 — 값의 진위, 선택지 중 하나를 고른 근거,
     범위를 그은 자리. 2항에서 이미 돌아간 검증을 여기 옮겨 적지 않는다.
     한 줄 형식: 체크박스 하나에 의견 하나 — "<주제> — <지금 고른 값과 그 근거>".
     **의견마다 상세가 따라붙고, 상세는 조각 둘이다** — `**배경**` 과 `**정할 것**` 이
     각각 단독 줄이다(없거나 하나뿐이면 종료코드 12). 검토자는 이 카드를 수행하지
     않았으므로 내부 기호(`L10`·`P5`·`S8`)만 던지면 판정할 재료가 없고, 재료가 있어도
     줄글 한 덩이면 필요한 부분만 골라 읽지 못한다.
       **배경** — 무엇이 문제인가. `- ` 목록으로, 항목 하나에 사실 하나. 기호를 풀어 쓰고
         항목 끝에 `원문: 파일:줄` 이나 링크를 건다. ①②… 로 늘어놓을 것은 항목으로 가른다.
         목록이 없으면 종료코드 12 — 줄글은 화면에서 한 문단으로 붙는다.
       **정할 것** — 정할 것 한 줄. 그 아래 갈래마다 대가와 결과를 표로 단다:
         | 선택지 | 대가 | 그러면 어떻게 되는가 |
       추천은 선택지 셀 맨 앞의 `**추천** ` 접두다. 고를 것이 없는 항목이면 표를 비운다.
     **올리기 전에 둘을 본다.** ① 이 의견이 카드 의도(원문·목적·이유·목표)와 이어지는가
     — 이어지지 않으면 올리지 않는다. 문제를 위한 문제는 판단 항목이 아니라 별도 카드다.
     ② 지시 원본보다 낮은 레이어로 내려가지 않았는가 — 유저가 제품 관점으로 지시했는데
     플래그 이름·함수 이름을 묻고 있으면 서술을 고칠 것이 아니라 올릴 것이 아니다.
     (SKILL.md 5.6 「판단 항목에 무엇을 올리는가」)
     비어 있으면 "기계가 다 판정했고 사람이 정할 것이 없다"는 뜻이다. 그 판단도
     착수한 쪽이 하는 것이지 검토자가 빈칸을 보고 추측할 일이 아니다.
     **승계 절(3-0)이 있으면 그것이 먼저 온다** — 다른 검토서에서 넘어온 의견이고,
     판정은 승계를 받은 이 문서 하나에서만 내려진다. -->

**의견마다 판정과 추가 의견이 따로 붙습니다.** 판정은 상태이고 추가 의견은 말입니다 — 승인/반려를 아직
안 정했어도 의견 하나에만 추가 의견을 달 수 있고, 반대로 의견 하나만 먼저 닫을 수도 있습니다.
`<번호>`는 의견 순서이고, 주제의 문구 일부로도 찾습니다.

```
# 판정 — 승인 · 반려 · 철회
python3 scripts/kanban.py review-judge <project-root> --card KAN-001-MJ3PE1 --item <번호> --verdict 승인
# 추가 의견
python3 scripts/kanban.py review-note <project-root> --card KAN-001-MJ3PE1 --item <번호> --text "<추가 의견>"
# 추가 의견을 반영하다 새 의견이 생겼으면 (맨 뒤에 붙어 앞 번호가 안 밀립니다)
python3 scripts/kanban.py review-item <project-root> --card KAN-001-MJ3PE1 --add "<주제>
  <상세>"
```

**전체 승인은 살아있는 항목이 전부 승인일 때만 섭니다**(철회는 분모에서 빠집니다). 하나라도
반려·추가 의견·미정이면 4항의 전체 승인도 `→ 완료` 이동도 종료코드 14로 거부됩니다.

- [ ] 조사 근거를 이 수준으로 받아들일 것인가 — 초록·검색 스니펫으로만 확인했고 주장마다 확인 수준 표지를 달았습니다
    - **배경**
      - 원문 지시는 「구조화에는 조사가 선행되어야 한다」와 「전문적 토대 위에 구조화」를 요구합니다.
      - 조사 때 원문 페이지 열람이 네트워크 정책에 막혀 논문·문헌 본문은 읽지 못했습니다. 원문: plugins/authoring-kit/skills/authoring-style/assets/STYLE_RESEARCH.md:14
      - 그래서 노트의 모든 주장에 [확인]·[추정] 같은 확인 수준 표지를 붙였습니다. 원문: plugins/authoring-kit/skills/authoring-style/assets/STYLE_RESEARCH.md:19
    - **정할 것**
      이 근거 수준으로 카드를 닫을 것인가.

    | 선택지 | 대가 | 그러면 어떻게 되는가 |
    | --- | --- | --- |
    | **추천** 이대로 받는다 | 분류 일부는 원문 대조 없이 선다 | 카드가 닫히고, 원문 대조는 필요할 때 별도 카드로 한다 |
    | 원문 대조 후 닫는다 | 열람이 되는 환경에서 조사를 다시 해야 한다 | 이 카드는 그때까지 검토에 머문다 |

    > **판정** — _아직 없습니다._

    > **추가 의견** — _아직 없습니다._

- [ ] 기본 점검 기준값을 설계 초기값 그대로 내보낼 것인가 — 코퍼스로 검증하지 않았고 편집기에서 층마다 고칠 수 있게 열어 두었습니다
    - **배경**
      - 어휘가 한 문장 안에서 몇 번 겹치면, 1,000자당 몇 번 나오면 경고할지의 기준값이 있습니다. 원문: plugins/authoring-kit/skills/authoring-style/assets/STYLE_RESEARCH.md:23
      - 이 값은 측정으로 정한 것이 아니라 설계할 때 둔 초기값입니다.
      - 이 저장소의 사람이 쓴 문서 17편에서는 경고가 나오지 않았고, 일부러 과장한 표본에서는 나왔습니다.
      - 전역 설정과 voice 설정에서 키 하나씩 덮어 고칠 수 있습니다. 원문: plugins/authoring-kit/scripts/style_registry.py:279
    - **정할 것**
      초기값 그대로 내보낼 것인가.

    | 선택지 | 대가 | 그러면 어떻게 되는가 |
    | --- | --- | --- |
    | **추천** 그대로 내보낸다 | 실제 글에서 경고가 너무 많거나 적을 수 있다 | 쓰면서 편집기로 조정하고, 조정한 값이 전역 설정에 쌓인다 |
    | 코퍼스로 먼저 맞춘다 | 검증용 글 묶음을 모으는 작업이 따로 든다 | 이 카드는 그때까지 닫히지 않는다 |

    > **판정** — _아직 없습니다._

    > **추가 의견** — _아직 없습니다._


## 4. 판정

<!-- 문서 하나에 대한 판정이다. **항목별로 갈리는 말은 여기 적지 않는다** — 3항 각 의견의
     「판정」과 「추가 의견」이 그 자리다. 여기 남는 것은 그 항목들이 전부 승인으로 닫혔다는
     사실 하나뿐이다.
     아래 「판정 이력」은 **덧붙기만 하는 이력**이다. 왕복이 돌면 줄이 쌓이고, 그것이 이 문서가
     무엇을 거쳐 승인에 닿았는지의 전부다 — 지우지 않는다. **판정에는 사유 칸이 없다** —
     승인은 대체로 덧붙일 말이 없고, 있다면 그것은 문서 전체가 아니라 그 항목에 대한
     말이라 3항의 「추가 의견」이 받는다.
     `review-judge --card KAN-001-MJ3PE1 --verdict 승인` 이 이 자리를 쓰고
     frontmatter 의 status 도 함께 고친다. 손으로 적어도 되지만, 그때는 수렴 검사를
     안 거치므로 `validate` 가 항목 판정과 어긋난 승인을 error 로 잡는다. -->

**판정**: (아직 없습니다)

**판정 이력**:

- 승인이면 → `apply --op move --id KAN-001-MJ3PE1 --to done` 뒤에 `main` 병합과 워크트리 정리(출력의 `cleanup`)
- 반려면 → `apply --op move --id KAN-001-MJ3PE1 --to doing` 뒤에 `doc-log --entry "<반려 사유>"`.
  요청서는 **지우지도 다시 뜨지도 않는다** — 고친 뒤 그 항목을 `review-judge --verdict 승인` 으로
  뒤집으면 같은 문서에서 수렴한다. 1·2항이 낡았으면 `review-init --refresh` 로 그 두 항만 간다.
