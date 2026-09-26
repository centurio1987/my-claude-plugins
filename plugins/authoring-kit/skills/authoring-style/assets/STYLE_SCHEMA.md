# 문체 설정 스키마 (`authoring-kit/style@1`)

문체 설정은 **세 벌이 겹쳐** 유효값이 된다. 뒤가 앞을 덮는다.

```
skills/authoring-method/assets/style/lexicon.json      ① 기본 카탈로그 — 분류 체계·기능 태그·기본 어휘 (읽기 전용)
skills/authoring-method/assets/style/qualitative.json  ① 정성 분류 체계 — 9범주 41말단·판정 질문·지시 예시 (읽기 전용)
~/.claude/authoring/global/style.json                  ② 전역 설정 — 모든 voice 가 계승한다
~/.claude/authoring/voices/<id>/style.json             ③ voice 설정 — 전역을 계승하고 확장한다
```

②·③ 은 **차분만** 저장한다. 기본값을 통째로 복사하면 플러그인이 분류 체계를 고쳐도 사용자 파일이 옛 판본으로 굳는다.
②·③ 은 모양이 같다.

```json
{
  "$schema": "authoring-kit/style@1",
  "schema_version": 1,
  "lexicon": {
    "overrides":  { "<항목 id>": { "weight": -2, "enabled": true, "reason": "…" } },
    "categories": { "<분류 id>": { "enabled": false, "check": { "density_per_1000": 4, "stack": 2 } } },
    "add":        [ { "id": "…", "category": "…", "forms": ["…"], "weight": -1, "functions": ["…"] } ]
  },
  "directives": {
    "overrides":  { "<지시 id>": { "enabled": false, "text": "…", "gate": { "enabled": true, "level": "MUST" } } },
    "add":        [ { "id": "…", "category": "stance.certainty", "text": "…", "example": { "good": "…", "bad": "…" },
                      "enabled": true, "gate": { "enabled": false, "level": "SHOULD" } } ],
    "categories": [ { "id": "tenor.office", "parent": "tenor", "label": "사내 보고 말투",
                      "definition": "…", "questions": ["…"] } ]
  }
}
```

## 정량 — 어휘 목록

### 가중치

| 값 | 이름 | 모델에게 가는 지시 | 기계 판정(`scan_lexicon.py`) |
| --- | --- | --- | --- |
| -3 | 금지 | 쓰지 않는다 | 1회부터 적발 |
| -2 | 강한 절제 | 꼭 필요한 자리에서만, 글 전체에서 한두 번 | 1,000자당 0.5회 초과(최소 1회 허용) |
| -1 | 절제 | 대안이 있으면 대안을 쓴다 | 1,000자당 1.5회 초과(최소 2회 허용) |
| **0** | **보통** | 지시 없음 | 세기만 한다 |
| +1 | 선호 | 같은 뜻이면 이쪽을 고른다 | 사용 횟수 보고 |
| +2 | 적극 | 자리가 오면 쓴다 | 한 번도 안 쓰면 알림 |
| +3 | 표지 | 이 목소리의 표지다 | 한 번도 안 쓰면 경고 |

**0 이 보통이다.** 양수는 보통보다 적극, 음수는 보통보다 소극. 가중치는 -3~+3 정수다.
'의'·'-들'처럼 원래 자주 쓰는 말은 항목에 `budget`(`per_1000`·`min`)을 두어 허용량을 따로 잡는다.

### 필터 — `enabled`

`enabled: false` 는 항목을 **채택 목록에서 뺀다** — 모델 지시에도 스캔에도 안 들어간다.
분류 단위로도 끌 수 있고(`categories[id].enabled`), 끄면 하위 분류까지 꺼진다.

### 항목 필드

| 필드 | 내용 |
| --- | --- |
| `id` | 소문자·숫자·점·하이픈. 사용자가 추가한 항목은 편집기가 `g.`(전역)·`v.`(voice) 로 시작하게 만든다 |
| `category` | 형식 분류 노드 하나 |
| `forms` / `regex` | 셀 대상. 둘 중 하나. `regex` 면 `label` 로 사람이 읽는 이름을 준다 |
| `except` | 이 정규식이 걸리는 문장은 세지 않는다(예: '축'의 좌표 용법) |
| `functions` | 기능 태그 여럿 |
| `mode` | `count` · `sentence-initial` · `sentence-final` · `paragraph-initial`. 없으면 분류 기본값 |
| `boundary` | `word`(어절 머리에서만) · `none`. 없으면 분류 기본값 |
| `alternatives` | 대안. 모델 지시와 스캔 보고에 함께 나간다 |
| `l0` | L0 에서 온 항목의 기원 `{code, axis, scanner?}`. **플러그인 기본값만 갖는다** |

### 분류 점검 — 층에서 조정한다

분류가 선언한 점검(`check.stack` 한 문장 겹침, `check.density_per_1000` 분류 밀도)은 **설계 초기값**이라
층마다 `categories[id].check` 로 덮는다. 밀도는 3회 미만이면 판정하지 않는다(짧은 글에서 튀지 않게).
양수 가중치 항목은 분류 점검에서 빠진다 — 즐겨 쓰겠다고 한 말을 과다로 세면 판정이 뒤집힌다.

### L0 에서 온 항목 — 면제 규칙

| 기원 | 층이 할 수 있는 것 |
| --- | --- |
| hard floor(`grammar` 등) | 가중치를 **내리기만** 한다. 올리거나 끄면 거부된다. 그 항목이 든 분류도 끌 수 없다 |
| `machine-rhythm` | 끄거나 **양수로 올리면 그 항목에 대한 면제**다 — `reason` 이 없으면 거부된다 |

`machine-rhythm` 항목 면제는 voice 의 코드 단위 `waivers` 보다 좁다. `W5` 전체가 아니라 '다양한' 하나만 풀 수 있다.
L0 스캐너(`scan_ai_style.py --voice`)는 면제된 항목을 목록에서 빼고 잰다.

## 정성 — 지시 목록

| 필드 | 내용 |
| --- | --- |
| `id` | 소문자·숫자·점·하이픈. 해석 결과에서 `Q:<id>` 로 불린다 |
| `category` | 정성 분류의 말단 하나(`stance.certainty` 등, 또는 아래 사용자 범주). 말단의 축이 곧 이 지시의 축이다 — L1 넷 중 하나 |
| `text` | 모델에게 들어가는 지시. 비울 수 없다 — 끄려면 `enabled: false` |
| `example` | `{good, bad}` 예문(선택). 추상 형용사만으로는 재현되지 않는다 |
| `gate` | `{enabled, level}`. 켜면 게이트 채점 항목이 된다. `level` 은 `MUST` · `SHOULD` |

### 사용자 범주 — `directives.categories`

플러그인 분류(9범주 41말단)에 없는 범주가 필요하면 층에서 직접 만든다. **기존 상위 9개 밑의 하위로만** 선다.

| 필드 | 내용 |
| --- | --- |
| `id` | `<상위>.<이름>` 꼴. 소문자·숫자·점·하이픈. 플러그인 분류나 아래 층 범주와 겹치면 안 된다 |
| `parent` | 상위 9개(`tenor` · `stance` · `cadence` · `pacing` · `figure` · `engage` · `illus` · `frame` · `diction`) 중 하나 |
| `label` | 편집기·해석 결과에 보이는 이름. 비울 수 없다 |
| `definition` | 정의(선택) |
| `questions` | 판정 질문 목록(선택). 이 범주에 묶인 지시를 게이트에 붙이면 채점 항목 아래에 실린다 |

**축은 적지 않는다** — 상위에서 물려받는다. 사용자가 축을 고르면 L1 이 아닌 축을 가리키는 범주가 생기고, 갈래 소유권이 거기서 깨진다.
전역에서 만든 범주는 모든 voice 가 쓰고, voice 에서 만든 범주는 그 voice 만 쓴다. voice 는 전역 범주를 고치지 않는다 — 전역에서 고친다.
지시가 쓰는 범주는 지울 수 없다. **voice 가 쓰는 전역 범주를 지우는 전역 저장은 편집기가 거부한다.**

**게이트에 붙은 지시는 채점자가 읽고만 판정한다.** 스크립트·정규식·카운터를 만들지 않는다.
판정 규칙은 `qualitative.json` 의 `judging.rules` 에 있다.

`preserve` voice 에서는 지시가 "새로 쓰는 지침"이 아니라 **다듬을 때 지킬 색**으로 렌더된다.

## 검증 — 저장 전에 막는다

`authoring.py style validate` 와 편집기의 저장이 같은 검사를 한다. **실패하면 저장하지 않는다** — 조용히 고쳐 쓰지 않는다.

- 가중치가 -3~+3 정수인가, 덮을 대상이 아래 층에 있는가, 추가 id 가 겹치지 않는가
- hard floor 항목을 올리거나 끄지 않았는가, `machine-rhythm` 항목 면제에 `reason` 이 있는가
- 정규식이 컴파일되는가, 분류·기능 태그·정성 분류가 실재하는가
- 정성 분류의 축이 L1 소유인가, 지시문이 비지 않았는가, 게이트 등급이 `MUST`·`SHOULD` 인가
- 사용자 범주의 상위가 실재하는가, id 가 `<상위>.<이름>` 꼴이고 겹치지 않는가, 이름이 있는가, 축을 적지 않았는가

## 재현성

`authoring.py lock` 이 기본 카탈로그 두 파일과 전역 설정의 해시를 `style` 묶음에 고정한다.
voice 별 `style.json` 은 그 voice 의 해시에 들어간다. `resolve --frozen` 은 어긋나면 집필하지 않는다.
