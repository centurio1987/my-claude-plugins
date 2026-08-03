---
name: authoring-write
description: >
  등록된 글 명세(spec)와 퍼소나(voice)에 따라 글을 집필하는 오케스트레이터 스킬.
  공통 원칙·퍼소나 톤·글 종류 규격을 한 벌로 해석해 집필 에이전트에 넘기고,
  외부 검토와 품질 게이트까지 완주시킨다. "이 명세로 글 써줘", "가이드 집필해줘",
  "authoring-write <spec>", "명세대로 초안 만들어줘" 같은 표현에 반응한다.
  명세가 아직 없으면 `authoring-spec`, 퍼소나가 없으면 `authoring-voice` 로 분기한다.
argument-hint: <spec-id> [주제 또는 입력 파일]
metadata:
  version: "0.1.0"
---

# authoring-write (집필 오케스트레이터)

등록된 **명세 + 퍼소나 + 공통 원칙**으로 글을 쓴다. 이 스킬은 **규칙 전문을 읽지 않는다** —
`authoring.py resolve --profile main` 이 만든 요약(≈120줄)만 보고 진행을 지휘하고,
조항 전문은 집필·채점 서브에이전트가 `authoring-method` 로 따로 로드한다.

> 이 분리가 중요한 이유: L0 네 문서 전문은 1000줄이 넘는다. 메인이 그걸 안고 가면
> 정작 글을 쓸 예산이 남지 않는다.

## 입력 / 출력 계약

- **입력**: `<spec-id>` + 집필 대상(주제·문제명·소스 메모 경로).
- **출력**: `paths.json` 의 `dirs` 가 가리키는 위치에 초안 1편 + 품질 게이트 보고.
- **불변 원칙**: 미검증 수치·출처 없는 단정 금지(L0 `evidence`). 활성 voice 의 `forbid` 위반 금지.
  **자동 통과 없음** — 게이트 미통과 상태로 끝내지 않는다.

## 동작 순서

### 1. 준비 확인

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/authoring.py status
```

- `specs` 에 대상 spec 이 없으면 → **`authoring-spec` 으로 분기**해 먼저 등록한다.
- spec 의 `voice.default` 가 `voices` 에 없으면 → **`authoring-voice` 로 분기**한다.
- `status` 가 `draft`/`undefined` 인 voice 면 그 사실을 사용자에게 알리고 진행 여부를 묻는다.

### 2. 규칙 해석 (메인용 요약)

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/authoring.py resolve \
  --voice <voice> --spec <spec-id> --profile main
```

- **비-0 종료면 멈춘다.** `CONFLICT` 는 두 층이 같은 축을 주장한다는 뜻이고,
  조용히 한쪽을 이기게 하면 안 된다. 사용자에게 충돌 내용을 그대로 보여주고 판단을 받는다.
- 여기서 얻는 것: 항목 골격 · 범위 원칙 · voice 요약 · 걸려 있는 L0 코드 목록.

### 3. 자료 확보

주제에 사실 조사가 필요하면 **기존 `web-research:research` 에 위임**한다(이 플러그인은 리서치를 하지 않는다).
프로젝트에 이미 소스가 있으면(리서치 노트·raws·문제 정의) 그걸 읽어 쓴다.
**소스 없이 사실을 지어내지 않는다.**

### 4. 집필 위임

`Agent` 로 서브에이전트를 띄우고, 프롬프트에 반드시 담는다:

- 담당 **항목**(§2에서 얻은 골격)과 대상 주제.
- "**먼저 `authoring-method` 스킬을 호출**해 조항 전문(L0 원칙·문장·리듬 + voice 전문 + 항목별
  작성 방법)을 로드하라. 실패하면 `authoring.py resolve … --profile worker` 를 직접 실행하라."
- **조건부 항목 처리**: 해당 없으면 절을 통째로 지우고, **생략 사유는 게이트 보고에만** 남긴다.
  독자용 문서에 "해당 없음" 같은 집필 메타를 남기지 않는다.
- 산출 경로(`paths.json` 의 `dirs`)와 확장자.

긴 글이면 항목 묶음으로 나눠 여러 워커에 병렬 위임하되, **한 글 = 한 voice** 는 깨지 않는다.

### 5. 시각자료·엔진 블록

프로젝트가 소유한 스킬에 위탁한다(이 플러그인은 이미지를 만들지 않는다).
`paths.json` 의 `commands`·프로젝트 CLAUDE.md 가 어느 스킬인지 알려 준다.

### 6. 외부 검토

spec 의 `gate.external_review.enabled` 가 참이면:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/review-external.sh --axes <spec의 axes> --redact <프로파일> <파일>
```

- `redact` 프로파일이 `none` 이 아니면 **전송 전에 치환**된다 — 개인정보가 든 글은 그냥 보내지 않는다.
- 실패 정책은 spec 의 `failure_policy`(`hard-fail` | `warn`)를 따른다.
  한쪽 도구만 응답한 부분 성공은 **경고와 함께 진행**하고 어느 쪽이 빠졌는지 보고에 남긴다.

### 7. 품질 게이트

`authoring-gate` 에 넘긴다. 통과할 때까지 **최대 3라운드**. 3라운드에도 MUST 가 남으면
멈추고 사람에게 넘긴다 — 라운드를 소진했다고 통과시키지 않는다.

### 8. 종료 보고

- 만든 파일 경로 · 사용한 voice/spec · **`resolve --profile worker` 해시**
  (어떤 규칙 조합으로 쓰였는지 추적 가능해야 한다).
- 게이트 결과(MUST 통과 수 · SHOULD 미흡 수 · 문체 등급).
- **생략한 조건부 항목과 그 사유.**
- 외부 검토에서 도구가 빠졌으면 그 사실.

## 참조

- `../authoring-method/SKILL.md` — 조항 전문(워커가 로드, 메인은 읽지 않는다)
- `../authoring-spec/SKILL.md` · `../authoring-voice/SKILL.md` — 미등록 시 분기 대상
- `../authoring-gate/SKILL.md` — 채점·보완 루프

## 주의

- **본문을 이 스킬에서 직접 쓰지 않는다.** 집필은 워커에 위임한다 — 메인이 전문을 안 읽기 때문이다.
- 플러그인이 설치돼 있지 않거나 `authoring.py` 가 없으면 **명확히 실패**한다.
  구 경로로 조용히 폴백하지 않는다 — 어떤 규칙으로 쓰였는지 알 수 없게 된다.
- 외부 작업(웹·codex·agy)은 실패할 수 있다. 실패를 숨기지 말고 보고에 남긴다.
