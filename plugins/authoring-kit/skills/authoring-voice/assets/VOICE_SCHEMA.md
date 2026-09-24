# voice 스키마 (`authoring-kit/voice@1`)

한 저자·퍼소나가 **어떻게 말하는가**를 담는다. **voice 는 프로젝트를 넘나든다** —
같은 퍼소나를 프로젝트마다 따로 만들지 않는다.

## 파일 두 개 (+ 선택 하나)

```
~/.claude/authoring/voices/<id>/
  voice.json   기계 판독 — 축·파라미터·면제
  voice.md     사람·에이전트 판독 — 문체 규칙 N개(예문 포함) + 금지 목록
  style.json   (선택) 문체 설정 — 전역(`~/.claude/authoring/global/style.json`)을 계승·확장하는 차분
```

`style.json` 스키마는 `authoring-style` 스킬의 `STYLE_SCHEMA.md` 에 있다. 어휘 목록의 가중치(-3~+3)·필터와
정성 지시를 담는다. **면제 규칙은 여기와 같다** — L0 `machine-rhythm` 어휘를 끄거나 양수로 올리면 항목 단위 면제라
`reason` 이 필요하고, hard floor 어휘는 올릴 수 없다.

`voice.md` 형식은 **"문체 규칙 N개(각 규칙 + 예문) + 금지 목록"** 이다.
두 프로젝트에서 이미 이 형식으로 굴러가고 있었고, 그대로 표준으로 삼았다.

## 최상위 필드

| 필드 | 필수 | 내용 |
| --- | --- | --- |
| `$schema` | ✓ | `"authoring-kit/voice@1"` |
| `schema_version` | ✓ | 정수 |
| `id` | ✓ | kebab-case. 디렉토리명과 같아야 한다 |
| `label` | ✓ | 사람이 읽는 이름 |
| `kind` | ✓ | `human` \| `ai-persona` — **누구인가** |
| `usage` | ✓ | `generate` \| `preserve` — **어떻게 쓰이는가** |
| `status` | ✓ | `defined` \| `draft` \| `undefined` |
| `source` | ✓ | 어디서 뽑았는가 — 역추출이면 모수까지 |
| `axes` | ✓ | `register` · `rhythm` · `device` · `lexicon` |
| `params` | | 수치 파라미터 |
| `waivers` | | 공통 원칙 면제 |
| `forbid` | ✓ | 이 퍼소나가 절대 하지 않는 것 |
| `used_by` | | 어느 프로젝트·저자 id 가 이 voice 를 쓰는가 |

## `usage` — 쓰는 목소리인가, 지키는 목소리인가

`kind` 로는 이걸 못 가른다. `yundeok` 은 사람이지만 AI 가 그 목소리로 이력서를 쓰고,
`ppangto`(빵관 토니) 도 사람인데 **AI 가 그 목소리로 쓰는 일은 없다** — 본인이 직접 쓴다.

| 값 | 뜻 | 집필 에이전트가 할 일 |
| --- | --- | --- |
| `generate` | AI 가 이 목소리로 **쓴다** | 축 선언을 집필 지침으로 따른다 |
| `preserve` | 사람이 쓴 글을 손볼 때 **지킬 색** | 새로 쓰지 않는다. 다듬을 때 이 표현들을 건드리지 않는 근거로만 본다 |

이 구분이 없으면 "사용자가 직접 쓰는 저자"의 문체를 생성 지침으로 오해한다.
`usage` 를 스키마에 박은 이유가 그 오해가 실제로 났기 때문이다.

## `status` — 셋을 구분하는 이유

| 값 | 뜻 | 게이트 동작 |
| --- | --- | --- |
| `defined` | 확정. 그대로 쓴다 | 정상 |
| `draft` | 역추출 초안. **사람 승인 전** | 경고 — 이 voice 로 발행하지 않는다 |
| `undefined` | 저자는 있는데 문체가 정의 안 됨 | 경고 — 집필 전에 정의하라고 알린다 |

`undefined` 를 **명시적으로 등록**하는 게 중요하다. 등록조차 없으면 "이 퍼소나는 문체가 없다"는
사실 자체가 어디에도 안 남고, 그 자리를 다른 저자의 문체가 조용히 메운다.

## `axes` — 이 넷만 쓴다

```json
{
  "register": "종결 톤·경어체·격식. 글 종류에 따라 바뀌는지, 한 글 안에서 섞는지",
  "rhythm":   "문장 호흡·길이 분포·전개 보폭",
  "device":   ["장치를 kebab-case 로 나열", "예: ascii-art-after-concept"],
  "lexicon":  "어휘군·인용 습관·연결어"
}
```

**여기 없는 축을 쓰면 `validate` 가 갈래 위반으로 막는다.**

- `structure`(항목·순서) → 글 명세(L2) 소관
- `evidence`·`grammar`·`comprehension` → 공통 원칙(L0) 소관, 불가침
- `machine-rhythm` → L0 가 탐지, voice 는 `waivers` 로 면제만

`device` 를 배열로 두는 이유: 채점(V3)이 "선언한 장치가 실제로 쓰였는가"를 세야 하고,
산문이면 셀 수 없다. **선언만 있고 본문에 하나도 없으면 목소리가 없는 글이다.**

## `params`

```json
{ "bold_per_paragraph": 2, "max_subordinate_clauses": 3 }
```

공통 원칙이 참조하는 수치다. L0 는 **"볼드는 아껴야 산다"** 까지만 정하고
**몇 개까지인지는 voice 가 정한다.** 이렇게 나눠야 규칙은 공통이면서 수치는 저자별이 된다.

## `waivers` — 신중하게

```json
{ "code": "R2", "target": "L0:machine-rhythm",
  "reason": "만연체가 기본 호흡이다",
  "limit": "종속절 4개 이상이면 waiver 해제" }
```

| 필드 | 규칙 |
| --- | --- |
| `code` | 면제할 L0 코드 |
| `target` | **`L0:machine-rhythm` 만 가능.** `evidence`·`grammar`·`comprehension` 은 hard floor 라 거부된다 |
| `reason` | **없으면 거부된다.** 조용한 면제는 만들지 않는다 |
| `limit` | **반드시 적는다.** 면제에도 한계가 있어야 한다 — 무제한 면제는 규칙을 지우는 것이다 |

면제가 필요 없으면 `[]` 로 둔다.
**다른 퍼소나의 면제를 물려받지 않는 것이 이 분리의 요점이다.**

## `source` — 역추출이면 모수까지

```json
{ "origin": "reverse-extraction",
  "refs": ["…에서 추출"],
  "corpus": { "included": ["시리즈 A(6편)", "시리즈 B(3편)"],
              "excluded": [{"what": "시리즈 C(4편)", "why": "파이프라인 우회 손집필 — 퍼소나 미적용이 기록됨"}] },
  "note": "…" }
```

**뺀 글과 그 이유를 반드시 적는다.** 나중에 "왜 이 문체가 이렇게 정의됐나"를 되짚을 유일한 단서다.

## `used_by`

```json
{ "projects": ["centurio1987.github.io", "code_test"], "author_ids": ["ppangtolab-teacher"] }
```

같은 퍼소나가 여러 프로젝트에서 쓰이면 여기에 모두 적는다.
**프로젝트마다 voice 를 새로 만들지 않는다** — 그게 지금 고치고 있는 복제 문제다.
