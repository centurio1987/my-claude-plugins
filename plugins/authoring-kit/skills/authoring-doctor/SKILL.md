---
name: authoring-doctor
description: >
  집필 설정의 **구조적 문제를 진단**하는 스킬. 같은 이름 스킬이 여러 레벨에 있어 조용히 가려지는지,
  voice 없는 저자로 글이 나가고 있는지, 공통 원칙에 특정 저자 문체가 새어 들었는지,
  lock 이 낡았는지를 검사한다. "집필 설정 점검해줘", "authoring-doctor", "왜 규칙이 안 먹지",
  "설정 진단해줘", "스킬이 이상하게 로드돼" 같은 표현에 반응한다.
argument-hint: [프로젝트 경로]
metadata:
  version: "0.1.0"
---

# authoring-doctor (진단)

집필이 **조용히 잘못 돌아가는** 상태를 찾는다. 여기서 잡는 것들은 전부 에러 없이 흘러가기 때문에
결과물을 봐야 알아차리게 되는 종류다.

## 검사 항목

### 1. 스킬 shadowing — 개정이 조용히 무효화되는가

같은 이름의 스킬이 **유저(`~/.claude/skills/`) · 프로젝트(`.claude/skills/`) · 플러그인**
세 레벨에 있으면 우선순위가 높은 쪽이 이기는데, **어느 것이 로드됐는지 표시되지 않는다.**
프로젝트에서 스킬을 고쳐도 실전에서는 구버전이 도는 사고가 실제로 있었다.

```bash
ls ~/.claude/skills/ 2>/dev/null
ls <project>/.claude/skills/ 2>/dev/null
```

동명 스킬이 둘 이상 있으면 **어느 쪽이 canonical 인지 정하고 나머지를 정리하라고 보고**한다.
플러그인 스킬은 `authoring-` 프리픽스라 충돌하지 않지만, 프로젝트 스킬끼리는 충돌할 수 있다.

### 2. voice 없는 저자 — 목소리가 비어 있는 글

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/authoring.py list voices
```

- `status` 가 `undefined`/`draft` 인 voice 로 발행된 글이 있는가.
- 프로젝트의 저자 레지스트리(있다면)에 있는 id 중 **voice 가 등록되지 않은 것**이 있는가.
- 산출물 frontmatter 의 저자 필드가 **비어 스키마 기본값에 의존**하고 있는가
  — 기본값이 사람 저자면, AI가 쓴 글이 사람 이름으로 나가고 AI 표기도 붙지 않는다.

### 3. 축 위반 — 규칙이 잘못된 층에 있는가

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/authoring.py validate --all
```

- 공통 원칙(L0) 문서가 `register`/`rhythm` 같은 퍼소나 축을 선언했는가.
- spec 의 `principles` 가 퍼소나 축을 침범했는가.
- 면제(waiver)가 hard floor 를 겨냥했는가, 사유 없이 선언됐는가.

### 4. 저자 문체 유출 — 공통 원칙에 특정 저자가 남았는가

**이게 이 도구가 만들어진 이유다.** 한 저자의 문체가 공통 원칙에 섞이면 모든 퍼소나에 강제된다.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/authoring.py resolve --voice <A> --profile worker > /tmp/a.md
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/authoring.py resolve --voice <B> --profile worker > /tmp/b.md
```

A 의 고유 표지(저자명·전용 어휘·전용 장치)가 B 의 해석 결과에 **하나라도 있으면 유출**이다.
어느 L0 문서에서 왔는지 찾아 그 규칙을 L1 으로 내린다.

`fixtures/test_layer_separation.py` 가 같은 검사를 자동으로 한다.

### 5. 규칙 유실 — 이관 중 사라진 것

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/trace_rules.py verify --inventory <인벤토리> --root <배치 루트>
```

유실·미분류·UNTAGGED 가 0이어야 한다. **DROP 은 사유가 붙어 있어야** 한다 —
사유 없는 DROP 은 조용한 유실이다.

### 6. 레거시 플레이스홀더 잔존

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_placeholders.py check <파일> --stage final
```

발행물에 미해결 슬롯·집필 지시·마커가 남아 있는가. 신규 템플릿이 `std-v1` 을 쓰는가.

### 7. lock 이 낡았는가

`resolve` 가 stale 을 보고하면 규칙이 바뀐 뒤 다시 해석하지 않은 것이다.
그 상태로 쓴 글은 **어떤 규칙 조합으로 쓰였는지 추적할 수 없다.**

## 보고 형식

항목마다 **정상 / 경고 / 문제** 로 판정하고, 문제면 **무엇을 어떻게 고칠지** 한 줄로 낸다.
문제가 없으면 그냥 정상이라고 말한다 — 없는 문제를 만들어 내지 않는다.

## 주의

- 이 스킬은 **진단만 한다.** 고치는 것은 사용자 확인 후 해당 스킬(`authoring-spec`·
  `authoring-voice`)이나 직접 편집으로 한다.
- shadowing 검사에서 **파일을 지우자고 먼저 제안하지 않는다.** 어느 쪽이 최신인지는 사용자가 안다.
