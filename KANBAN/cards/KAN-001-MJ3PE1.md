---
card: KAN-001-MJ3PE1
title: authoring-kit 0.4.0 — 문체 설정 체계화(전역→voice 계승·어휘 가중치·정성 지시·편집기)
created: 2026-09-26
---

# KAN-001-MJ3PE1 — authoring-kit 0.4.0 — 문체 설정 체계화(전역→voice 계승·어휘 가중치·정성 지시·편집기)

## 전략
**소급 기록이다.** 작업은 카드 등록 전에 `claude/beautiful-mccarthy-kxg2nl` 에서 먼저 수행됐고(3e1ada8), 이 카드와 실행 문서는 그 뒤에 manage-kanban 정의로 옮겨 적은 것이다. 착수 전 계획(배치 문서·계획 리포트)은 당시 만들지 않았다 — 아래 절은 실제로 한 일을 재구성한 것이지 사전 계획이 아니다.

- **접근** — voice 의 목소리 중 관리할 수 있는 부분을 정량(어휘 목록: 가중치 -3~+3 · 필터)과 정성(지시 목록: 게이트에 붙으면 읽기로만 판정) 두 갈래로 떼고, 플러그인 기본값 → 전역(`~/.claude/authoring/global/style.json`) → voice(`voices/<id>/style.json`) 3층으로 겹친다. 층은 차분만 저장한다.
- **조사 선행** — 분류 체계는 조사 결과로 짰다. 형식 축은 학교문법 5언 9품사·어미 체계, 기능 축은 Hyland 메타담화 + 번역투 연구, 정성 분류는 Halliday·Hyland·Martin & White·이태준·Williams 등(`plugins/authoring-kit/skills/authoring-style/assets/STYLE_RESEARCH.md`).
- **제약** — 갈래 소유권 유지(정성 범주는 L1 축 하나씩), hard floor 는 어떤 층도 못 올림, 표준 라이브러리만, 조용한 면제 금지(사유 필수), 기존 L0 스캐너 판정 불변.
- **버린 대안** — 기본값을 사용자 파일로 복사(업데이트 시 옛 판본으로 굳음) · 형태소 분석기 도입(의존성 추가 — 정규식+예외 문맥으로 대체) · 한자어 비율 지표(단독 근거 없음) · 번역투 일괄 금지(수정안 부적절 사례 — 금지는 이중 피동·'에의' 둘로 한정).
- **한계** — 조사는 원문 열람이 막혀 검색 스니펫으로만 확인했고, 밀도·겹침 기준은 설계 초기값이다.

## 실행 계획
- [x] `S1` 조사 — 정량(한국어 어휘 분류·번역투 합의·메타담화)·정성(문체 요소 분류) 병렬 조사. 완료 기준: 확인 수준 표지가 붙은 노트 2편
- [x] `S2` 레지스트리 — `style_registry.py` 3층 병합·출처 추적·검증·렌더·가중치 스캔. 완료 기준: hard floor·사유 없는 면제가 저장 전에 거부된다
- [x] `S3` L0 스캐너 이관 — `scan_ai_style.py` 하드코딩 어휘(W·H·D) → 카탈로그. 완료 기준: 이관 전후 같은 입력에 같은 적발
- [x] `S4` 카탈로그 — `lexicon.json`(형식 45분류·기능 28태그·285항목), `qualitative.json`(9범주 41말단). 완료 기준: `style validate` 통과, 사람 문서 17편에서 적발 없음·과장 표본에서 적발
- [ ] `S5` 통합 — `authoring.py` resolve·validate·lock·`style` 서브커맨드, `scan_lexicon.py`. 완료 기준: resolve 가 유효 설정을 L1 절에 싣고 lock 이 어긋남을 안다
- [ ] `S6` 편집기 — `style_server.py` + `ui/style-editor.html`. 완료 기준: 브라우저로 편집·저장·거부·미리보기·시험 스캔, 폰 너비 가로 스크롤 0
- [ ] `S7` 문서 — `authoring-style` 스킬·스키마·조사 종합, gate V5·V6, rubric·voice·method·doctor·README, 0.4.0. 완료 기준: 끊어진 assets 참조 없음
- [ ] `S8` 검증 — `test_style.py` 신설, 기존 스위트 재실행. 완료 기준: 새 스위트 전부 통과, 기존 실패는 이전부터 있던 것만

## 검증
- `python3 plugins/authoring-kit/fixtures/test_style.py` → `통과 92 · 실패 0` (계승·검증·가중치 스캔·L0 항목 면제·resolve·lock·편집기 API)
- `test_scanner.py` · `test_linter.py` 통과, 대역 voice 로 돌린 `test_layer_separation.py` 32/32 (voice 간 누출 없음)
- `authoring.py style validate` → 정상
- 규칙 하나를 끈 돌연변이 실행에서 `test_style.py` 가 5건 실패 — 테스트가 실제로 잡는다
- Playwright 로 편집기 전체 흐름·라이트/다크·390px 폭 확인
- 알려진 실패(이 카드와 무관, 이전부터): `test_plugin_shape.py` 의 `authoring-write: 142줄 ≤ 130`

## 수행 내역
<!-- KANBAN:LOG append-only — 아래로만 덧붙인다. 위를 고치지 않는다. -->
- 2026-09-26T14:06 · s:c2291411 — `전략` 섹션 교체
- 2026-09-26T14:06 · s:c2291411 — `실행 계획` 섹션 교체
- 2026-09-26T14:06 · s:c2291411 — `검증` 섹션 교체
- 2026-09-26T14:06 · s:c2291411 — 소급 기록 — 아래 S1~S8 은 2026-09-24 claude/beautiful-mccarthy-kxg2nl 에서 먼저 수행한 것(3e1ada8). 배치 문서·계획 리포트·work 태그는 당시 만들지 않았다
- 2026-09-26T14:06 · s:c2291411 · S1 doing — 착수
- 2026-09-26T14:06 · s:c2291411 · S1 done — 정량·정성 조사 에이전트 병렬 — 노트 2편(lexicon-notes 588줄·qualitative-notes 550줄), 원문 열람 차단으로 스니펫 검증·확인 수준 표지
- 2026-09-26T14:06 · s:c2291411 · S2 doing — 착수
- 2026-09-26T14:06 · s:c2291411 · S2 done — style_registry.py — 기본값→전역→voice 병합·출처 추적, hard floor 상향·사유 없는 L0 면제 거부, 렌더·가중치 스캔(겹침·밀도·문말 점유율)
- 2026-09-26T14:06 · s:c2291411 · S3 doing — 착수
- 2026-09-26T14:06 · s:c2291411 · S3 done — scan_ai_style.py 어휘 목록을 카탈로그 l0.scanner 로 이관, 코퍼스 대조 동등(D7 힌트의 끊긴 참조만 제거), voice 항목 면제 반영
- 2026-09-26T14:06 · s:c2291411 · S4 doing — 착수
- 2026-09-26T14:06 · s:c2291411 · S4 done — lexicon.json 45분류·28기능·285항목(기본 음수는 합의 확인분만), qualitative.json 9범주 41말단·판정 규칙 — 과장 표본 적발·레포 문서 17편 무적발
