# 템플릿 — 수입과 생성

명세의 다섯 번째 입력이다. **이미 있는 파일을 들여오거나**, **요구사항을 받아 만들거나** 둘 중 하나다.

## (a) 수입 — 파일이 이미 있을 때

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_placeholders.py import <템플릿> --out template.slots.json
```

### 파일은 옮기지 않는다

템플릿 파일은 **프로젝트에 그대로 두고 `paths.json.templates` 가 경로만 참조**한다.

```json
{ "templates": { "resume-html": "templates/이력서.template.html" } }
```

spec 은 `template_ref: "resume-html"` 로 그 키를 가리킨다. 이유 셋:

1. 6MB 번들 HTML·바이너리 `.pptx` 를 레지스트리에 복사하면 관리가 불가능해진다.
2. 템플릿은 프로젝트의 자산이다 — 프로젝트 git 이 이력을 갖는 게 맞다.
3. 같은 명세를 다른 프로젝트에서 쓸 때 `paths.json` 만 갈아 끼우면 된다.

### 슬롯을 항목에 대응시킨다

`template.slots.json` 의 각 슬롯이 spec 의 어느 `sections[].id` 에 해당하는지 맞춘다.

- **대응 안 되는 슬롯**이 있으면 물어본다 — 항목이 빠졌거나 슬롯이 죽은 것이다.
- **슬롯이 없는 필수 항목**이 있으면 물어본다 — 템플릿에 자리가 없다는 뜻이다.
- 레거시 표기가 감지되면 spec 의 `placeholders.legacy_accept` 에 넣는다.

### 파서가 못 읽는 파일

`.pptx` 는 `python-pptx` 가 필요하다. 없으면 린터가 **종료코드 2로 실패**한다 —
못 읽은 것을 "슬롯 0개, 깨끗함"으로 보고하지 않기 위해서다. 설치하거나, 그 템플릿은
수입하지 말고 **요구사항으로 다시 받는다.**

## (b) 생성 — 요구사항만 있을 때

### 받을 것

- **형식** — 마크다운·MDX·HTML·슬라이드·문서 중 무엇인가.
- **지면 제약** — 1페이지, N슬라이드, 분량 상한.
- **고정 문구** — 바꾸면 안 되는 제목·라벨이 있는가.
- **채울 자리** — ①에서 받은 항목과 대응시킨다.

### 만드는 규칙

1. **항목 순서대로** 골격을 세운다. `heading_fixed: true` 인 항목은 문구를 그대로 박고,
   아닌 항목은 `{{ id }}` 로 제목 자리를 연다.
2. 각 자리에 **집필 지시**(`@write`)를 단다. 지시에는 **직무**를 적는다 —
   "여기에 내용"은 없느니만 못하다. spec.md 의 해당 항목 설명을 한 줄로 압축해 넣는다.
3. 조건부 항목은 **조건 블록**으로 감싸거나, 생략 규칙을 지시에 적는다.
4. 슬롯 id 를 spec 의 항목 id 와 **반드시 맞춘다.**
5. 파일 타입에 맞는 표기를 쓴다(`PLACEHOLDER_STD.md`). `.mdx` 에 `{{ }}` 를 쓰면 빌드가 죽는다.

### 확인 후 저장

만든 템플릿을 **보여 주고 확인받은 다음** 프로젝트의 템플릿 디렉토리에 저장한다.

> 이 저장이 **명세 등록 워크플로 전체에서 프로젝트 트리에 쓰는 유일한 지점**이다.
> 나머지는 전부 `.claude/authoring/` 안에서 끝난다.

저장 후 `paths.json.templates` 에 키를 추가하고, spec 의 `template_ref` 가 그 키를 가리키게 한다.

## 검증

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_placeholders.py check <템플릿> --stage draft
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/authoring.py validate --spec <id>
```

- 린터: 조건 블록 짝이 맞는가, 표기가 파일 타입에 맞는가.
- validate: `template_ref` 가 `paths.json` 에서 해소되는가.

둘 다 통과해야 등록이 끝난 것이다.
