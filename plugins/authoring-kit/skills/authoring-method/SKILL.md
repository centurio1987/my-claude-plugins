---
name: authoring-method
description: >
  집필·채점 워커 서브에이전트가 호출하는 **내부 방법론 스킬**. 공통 원칙(L0)·퍼소나 voice(L1)·
  글 명세(L2)의 조항 전문과 품질 루브릭을 로드한다. 사용자가 직접 트리거하지 않으며
  (엔트리는 `authoring-write`), 워커가 문장을 쓰기 직전에 명시적으로 호출한다.
disable-model-invocation: true
metadata:
  version: "0.1.0"
---

# authoring-method (집필 방법론)

워커가 실제로 문장을 쓰거나 채점하기 전에 로드하는 규칙 묶음이다.
**메인 스레드는 이 스킬을 읽지 않는다** — 전문이 1000줄을 넘기 때문이다.

## 전문을 얻는 법

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/authoring.py resolve \
  --voice <voice> --spec <spec-id> --project <프로젝트> --profile worker
```

한 벌로 병합된 문서가 나온다. **이 결과를 그대로 따른다.** 세 층이 순서대로 들어 있다:

1. **L1 — 이 글의 목소리** (`register` · `rhythm` · `device` · `lexicon` + 금지 목록 + 면제 표)
2. **L2 — 이 글 종류의 명세** (항목별 작성 방법 + 범위 원칙)
3. **L0 — 공통 원칙** (원칙 · 자연스러운 한국어 · 기계 리듬 · 품질 루브릭)

해석이 실패하면(`CONFLICT`) 글을 쓰지 말고 그대로 보고한다.

## 요지 (상세는 해석 결과)

1. **갈래 소유권.** 어떤 톤·호흡·장치로 쓸지는 **L1 voice** 가 정한다. 어떤 항목이 어떤 순서로
   필요한지는 **L2 spec** 이 정한다. 사실·문장·박자는 **L0** 가 정한다.
   자기 층이 아닌 것을 넘겨짚지 않는다.
2. **hard floor.** `evidence`(미검증 수치·출처 없는 단정 금지) · `grammar`(번역투) ·
   `comprehension`(점진적 공개·약어 풀어쓰기)은 **어떤 voice도 면제받지 못한다.**
3. **면제는 machine-rhythm 뿐.** 해석 결과의 면제 목록에 있는 코드는 그 글에서 증상이 아니다.
   면제된 코드를 고치려 들지 마라 — 그게 저자의 색이다.
4. **한 글 = 한 voice.** 다중 화자 spec 이 아니면 목소리를 섞지 않는다.
5. **조건부 항목**은 해당 없으면 절을 지운다. 생략 사유는 **게이트 보고에만** — 독자용 문서에
   집필 메타를 남기지 않는다.
6. **검증되지 않은 값을 쓰지 않는다.** 수치·경로·명령 결과는 실행하거나 손으로 검산해 확인한다.
   확인 못 한 값은 그럴듯한 숫자로 메우지 말고 무엇을 확인해야 하는지 남긴다.

## 자가 점검 도구

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/scan_ai_style.py "<파일>"          # 기계 리듬 등급
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_placeholders.py check "<파일>" --stage draft|final
```

문체 등급 합격선은 **B 이상**이다. **면제된 코드는 세지 않는다.**

## 참조 파일

- `assets/L0_PRINCIPLES.md` — 사실(`evidence`) · 독자 이해(`comprehension`)
- `assets/L0_NATURAL_KOREAN.md` — 영어투(`grammar`)
- `assets/L0_MACHINE_RHYTHM.md` — AI 기계 리듬(`machine-rhythm`)
- `assets/QUALITY_RUBRIC.md` — 채점 프레임 + 공통 항목
- `assets/review-axes/*.md` — 외부 검토 3축 프롬프트(글 종류별)

## 주의

- 이 문서의 요지만 읽고 쓰지 마라. **반드시 `resolve --profile worker` 결과를 로드**한다 —
  voice 와 spec 이 무엇인지는 글마다 다르다.
- 자연스러움을 핑계로 목소리를 지우지 않는다. 그것이 이 파이프라인에서 가장 큰 실패다.
