# spec 스키마 (`authoring-kit/spec@1`)

한 종류의 글이 무엇으로 이루어지고 어떻게 쓰이는지를 담는다. **논리만 담는다** —
경로·빌드명령은 `paths.json` 이 갖는다.

## 파일 세 개

```
<project>/.claude/authoring/specs/<id>/
  spec.json            기계 판독 — 검증·해석에 쓰인다
  spec.md              사람·에이전트 판독 — 항목별 작성 방법
  template.slots.json  템플릿을 수입했을 때만
```

> **분담 규칙: 검증에 쓰이면 JSON, 집필에 쓰이면 MD.**
> 항목 목록은 양쪽에 있지만 JSON 은 id·필수·순서만, MD 는 그 id 를 **어떻게 채우는지** 산문이다.
> JSON 을 산문으로 채우면 diff 가 읽히지 않고, MD 를 기계가 파싱하려 들면 곧 깨진다.

## 최상위 필드

| 필드 | 필수 | 내용 |
| --- | --- | --- |
| `$schema` | ✓ | `"authoring-kit/spec@1"` |
| `schema_version` | ✓ | 정수. 필드 추가는 optional 만 → minor. 제거·의미 변경은 major + migrate |
| `id` | ✓ | kebab-case. 디렉토리명과 같아야 한다 |
| `label` | ✓ | 사람이 읽는 이름 |
| `version` | ✓ | 이 명세 자체의 semver |
| `source` | | 출처 이력. **경로가 들어가도 되는 유일한 곳** — 어디서 가져왔는지는 경로로 적을 수밖에 없고, 그 기록이 지워지면 이관을 나중에 검증할 수 없다 |
| `voice` | ✓ | `{default, allowed[], voice_map?}` |
| `sections` | ✓ | 항목 배열 |
| `principles` | ✓ | 이 글 범위의 원칙 |
| `conditional_rule` | | 조건부 항목을 어떻게 다루는지 한 문장 |
| `template` | | 템플릿 참조 |
| `placeholders` | | `{profile, legacy_accept[]}` |
| `gate` | | 채점·외부검토 설정 |

## `sections[]`

```json
{ "id": "about", "label": "About — 포지션별", "required": true, "order": 20,
  "heading": "## About — 포지션별", "heading_fixed": true,
  "container": false, "parent": null, "repeat": false,
  "condition": "…해당할 때만",
  "variants": { "by": "position", "keys": ["cto", "po"] } }
```

| 필드 | 뜻 |
| --- | --- |
| `id` | 점 표기로 계층을 만든다(`idea.proof`). `spec.md` 와 `principles` 가 이 id 로 항목을 가리킨다 |
| `required` | `false` + `condition` 이면 **조건부**. `false` + `condition` 없으면 선택 |
| `order` | 10 단위로 띄워 둔다 — 나중에 사이에 끼워 넣을 자리 |
| `heading_fixed` | 참이면 **문구를 바꾸면 안 된다.** 거짓이면 직무만 고정이고 문구는 내용에 맞춰 짓는다 |
| `container` | 자기 본문 없이 하위 항목만 담는 절 |
| `repeat` | 여러 번 반복되는 항목(경력 하나하나, 최적화 라운드) |
| `variants` | 같은 항목을 축(직무·대상)별로 여러 벌 쓸 때 |

## `principles[]`

```json
{ "code": "SP1", "level": "MUST", "axis": "evidence", "text": "raw 3소스의 항목 누락 0" }
```

- `level` — `MUST` | `SHOULD` | `IF-APPLICABLE`
- `axis` — **`structure` · `scope-principle` · `evidence` 만 쓸 수 있다.**
  `register`·`rhythm`·`device`·`lexicon` 은 퍼소나 소관이라 `validate` 가 막는다.
  막히면 그 원칙이 정말 이 글 종류의 것인지 다시 본다 — 목소리 얘기면 voice 로 가야 한다.
- `text` — 채점자가 그대로 읽고 판정할 수 있게 쓴다. 충족 위치를 알면 함께 적는다
  (예: *"`naive` 절의 시그니처 코드 블록으로 충족한다"*).

## `voice`

```json
{ "default": "ppangtolab-teacher", "allowed": ["ppangtolab-teacher"],
  "voice_map": { "인터뷰어": "ppangto", "인터뷰이": "ppangtolab-prof" } }
```

- `allowed` 밖의 voice 로 해석하면 `CONFLICT` 로 죽는다.
- `voice_map` 은 **다중 화자 글에서만**. 없으면 불변식 "한 글 = 한 voice" 가 적용된다.

## `template`

```json
{ "kind": "html-bundle", "template_ref": "resume-html",
  "slot_style": "ordinal", "slots_map": "template.slots.json",
  "outputs": [{ "format": "pdf", "page_limit": 1 }] }
```

`template_ref` 는 **`paths.json.templates` 의 키**다. 파일 경로를 직접 쓰지 않는다 —
그래야 같은 명세를 다른 프로젝트에서 쓸 수 있다.

## `gate`

```json
{ "rubric": "default", "max_rounds": 3,
  "external_review": { "enabled": true, "axes": "review-axes/resume.md",
                       "failure_policy": "hard-fail", "redact": "resume-pii" } }
```

- `redact` — 개인정보가 든 글은 **반드시** 프로파일을 지정한다. `none` 은 이미 공개된 내용에만.
- `failure_policy` — 외부 검토 도구가 둘 다 실패했을 때. `hard-fail` | `warn`.

## 하면 안 되는 것

- **경로·빌드명령을 `spec.json` 에 넣기.** `paths.json` 이 그 자리다(`source` 는 예외).
- **퍼소나 축을 `principles.axis` 에 쓰기.** `validate` 가 막는다.
- **문서 종류별 문체 농도를 spec 에 쓰기.** 농도는 spec 이 맞지만 **문체 자체**는 voice 다.
  "이 문서는 은유를 절제한다"는 spec, "이 저자는 은유를 즐긴다"는 voice.
