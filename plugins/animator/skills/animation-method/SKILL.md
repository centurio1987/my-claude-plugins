---
name: animation-method
description: >
  `animation-scout`(포착자)와 `animation-applier`(적용자) 워커 서브에이전트가 호출하는 **내부 방법론
  스킬**. 모션 적용 가이드·점수 체크리스트·구현 reference·출력 계약을 제공한다. 사용자가 직접
  트리거하지 않으며(엔트리는 `animate` 스킬), 워커가 포착/적용 직전에 명시적으로 호출한다.
disable-model-invocation: true
metadata:
  version: "0.1.0"
---

# animation-method (모션 방법론)

`animation-scout`/`animation-applier` 워커가 작업을 시작하기 전에 로드하는 규칙 묶음이다. 상세는 네
assets 파일을 **그대로 따른다** — 이 본문은 요지만 담는다.

## 따라야 할 파일

- `assets/SCORE_CHECKLIST.md` — **포착자·게이트웨이 공용** 가중치 score 체크리스트. 기준·구간 예시·
  임계값·정량 상한·무조건 제외 조건. 점수 산정과 통과 판정의 **단일 출처**. 반드시 그대로 따른다.
- `assets/ANIMATION_GUIDE.md` — 패턴 카탈로그(언제 쓰나/권장 토큰/성능·접근성/구현 스케치)와 베이크
  **모션 토큰**. 적용 구현의 기준. 반드시 그대로 따른다.
- `assets/REFERENCE_SPECS.md` — 사례·원칙 reference 스펙(파라미터·버전 호환). 구현 시 참조한다.
- `assets/OUTPUT_CONTRACT.md` — scout findings 형식 + applier 보고 형식. 반드시 그대로 따른다.

## 요지 (상세는 위 파일)

1. **포착(scout)**: 기존 모션 인벤토리 → 후보 식별 → `SCORE_CHECKLIST`로 점수화 → 후보마다 **1·2순위**를
   한 번에 제안(재고 라운드 없음). 파일 수정 금지.
2. **게이트웨이**: 1순위→2순위→제외 순으로 임계값 판정. 무조건 제외 조건은 점수 무관 제외.
3. **적용(applier)**: 스택·버전 감지 → 기존 의존성만(없으면 CSS 폴백) → transform/opacity +
   `prefers-reduced-motion` 폴백 → 기존 핸들러·접근성 보존 → **린트/빌드 검증 + 실패 시 자동 롤백**.
4. **토큰**: 사용자 제공 디자인 시스템/토큰이 베이크 기본값보다 우선. 기존 토큰 재사용 우선, 신규 최소화.
5. **금지/필수**: 추측·과잉 모션·출처 모호한 코드 복붙 금지. 정량 상한 준수. 검증·롤백을 숨기지 않는다.
