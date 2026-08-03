---
name: authoring-spec
description: >
  집필하려는 글의 **명세를 등록**하는 스킬. 항목 구성 · 항목별 작성 방법 · 해당 글 범위의 원칙 ·
  적용 퍼소나를 입력받고, 구체적인 템플릿 파일을 수입하거나 요구사항을 받아 템플릿을 생성한다.
  "이력서 형식 등록해줘", "글 명세 만들자", "이 글 종류 규격 등록", "authoring-spec",
  "템플릿 등록해줘", "새 문서 형식 정의" 같은 표현에 반응한다.
  등록 결과는 이후 `authoring-write` 가 그대로 따른다.
argument-hint: <spec-id> [참조할 기존 산출물 경로]
metadata:
  version: "0.1.0"
---

# authoring-spec (글 명세 등록)

한 종류의 글이 **무엇으로 이루어지고, 각 부분을 어떻게 쓰며, 어떤 원칙과 목소리를 따르는가**를
등록한다. 등록해 두면 그 뒤로는 `authoring-write` 가 매번 같은 규격으로 쓴다.

## 받는 것 다섯 가지

| 입력 | 저장 위치 | 형식 |
| --- | --- | --- |
| ① **항목** | `spec.json.sections[]` | id · label · required · order · heading · condition |
| ② **항목별 작성 방법** | `spec.md` | 항목마다 산문 한 절 |
| ③ **해당 글 범위의 원칙** | `spec.json.principles[]` | code · level · axis · text |
| ④ **적용 퍼소나** | `spec.json.voice` | default · allowed · (다중 화자면 voice_map) |
| ⑤ **템플릿** | `spec.json.template` + `paths.json.templates` | 파일을 **수입**하거나 요구사항으로 **생성** |

> **JSON / MD 분담: 검증에 쓰이면 JSON, 집필에 쓰이면 MD.**
> 항목 목록은 양쪽에 있지만 JSON은 id·필수·순서만, MD는 그 id를 **어떻게 채우는지** 산문이다.
> **경로·빌드명령은 spec 에 넣지 않는다** — 전부 `paths.json` 으로. 그래야 같은 명세를
> 다른 프로젝트에서 쓸 수 있다.

## 동작 순서

### 1. 상태 확인

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/authoring.py status
```

같은 id 의 spec 이 이미 있으면 **편집 모드**를 제안한다(덮어쓰기 전에 확인).

### 2. 역추출을 먼저 제안한다 (권장 기본값)

> "이미 쓰신 글이 있으면 거기서 명세를 뽑아 드릴까요?"

백지 인터뷰보다 정확하다. 그리고 **지금 쓰는 글을 그대로 재현**하는 것이 목표라면
현행 산출물에서 뽑는 것이 곧 그 목표다. 참조로 받을 수 있는 것:

- 기존 산출물 1~3편 (가장 좋다 — 실제로 통과한 글)
- 템플릿·캔버스 파일 (골격이 이미 고정돼 있으면 그대로 옮긴다)
- 기존 체크리스트 (③ 범위 원칙의 원천)

추출 결과는 **확인만 받고**, 빈 칸만 질문한다.

### 3. 인터뷰 (`AskUserQuestion`, ①~⑤ 순서)

- **① 항목** — 순서·필수 여부·헤딩 문구 고정 여부. 조건부 항목이면 **어떤 조건일 때 쓰는지**.
- **② 작성 방법** — 항목마다 "무엇을 하는 자리인가". 좋은 예/나쁜 예가 있으면 함께.
- **③ 범위 원칙** — 이 글 종류에서만 지켜야 할 것. 각각 MUST/SHOULD/IF-APPLICABLE 과
  축(`structure` · `scope-principle` · `evidence`)을 매긴다.
  **`register`·`rhythm`·`device`·`lexicon` 은 쓸 수 없다** — 퍼소나 소관이라 validate 가 막는다.
- **④ 퍼소나** — `authoring.py list voices` 결과에서 고르게 한다.
  없으면 그 자리에서 **`authoring-voice` 등록으로 분기**한다.
- **⑤ 템플릿** — 아래 두 경로 중 하나.

### 4. 템플릿 — 수입 또는 생성

**(a) 수입** — 이미 파일이 있을 때

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_placeholders.py import <파일> --out template.slots.json
```

슬롯을 추출해 항목과 대응시킨다. **템플릿 파일 자체는 프로젝트에 그대로 두고
`paths.json.templates` 가 경로만 참조**한다 — 6MB HTML 이나 바이너리 `.pptx` 를 레지스트리에 복사하지 않는다.

**(b) 생성** — 요구사항만 있을 때

사용자가 원하는 바(형식·분량·지면 제약·필요한 자리)를 받아 `sections[]` 와 `std-v1` 규약으로
템플릿 초안을 만든다. 확인을 받은 뒤 **프로젝트의 템플릿 디렉토리에 저장**한다.
→ 이 워크플로에서 **프로젝트 트리에 쓰는 유일한 지점**이다.

플레이스홀더 규약(`std-v1`)은 `assets/PLACEHOLDER_STD.md` 를 따른다.

### 5. 저장과 검증

```
<project>/.claude/authoring/specs/<id>/spec.json
<project>/.claude/authoring/specs/<id>/spec.md
<project>/.claude/authoring/specs/<id>/template.slots.json   (템플릿이 있을 때)
<project>/.claude/authoring/paths.json                        (없으면 함께 만든다)
```

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/authoring.py validate --spec <id>
```

검사하는 것: 스키마 버전 · **축 위반**(spec 이 퍼소나 축을 선언했는가) ·
principles 의 level·axis · voice 존재 · `template_ref` 가 `paths.json` 에서 해소되는가.

### 6. 왕복 확인

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/authoring.py resolve --voice <voice> --spec <id> --profile main
```

항목 골격과 범위 원칙이 실제로 실리는지 눈으로 확인하고 사용자에게 보여 준다.

### 7. 종료 보고

- 만든 파일 경로 · 항목 수(조건부 몇 개) · 원칙 수 · 적용 퍼소나 · 템플릿 처리(수입/생성).
- **역추출로 채운 것과 사용자가 직접 답한 것을 구분해서** 보고한다 —
  역추출은 추정이므로 나중에 다시 볼 근거가 된다.

## 참조

- `assets/SPEC_SCHEMA.md` — 필드별 의미와 제약
- `assets/INTERVIEW.md` — ①~⑤ 질문 문안
- `assets/TEMPLATE_AUTHORING.md` — 템플릿 생성 규칙
- `assets/PLACEHOLDER_STD.md` — `std-v1` 플레이스홀더 규약

## 주의

- **경로·명령을 spec 에 넣지 마라.** `paths.json` 이 그 자리다.
- 축을 잘못 매기면 `validate` 가 막는다. 막히면 **그 원칙이 정말 이 글 종류의 것인지** 다시 본다 —
  퍼소나 얘기라면 voice 로, 저자 불문이라면 L0 로 가야 한다.
- 조건부 항목의 **생략 규칙**을 반드시 정한다. "해당 없음"을 본문에 남길지 보고에만 남길지가
  글의 품질을 가른다.
