# REFERENCE_SPECS — 구현 reference (파라미터·버전 호환·출처)

빌드 시점(2026-06-24, KST)에 1차 표준 소스에서 베이크한 reference다. **원칙·패턴·파라미터 수준**으로만
정리한다(코드 복붙·모사 금지). 구현 시 `ANIMATION_GUIDE.md`와 함께 참조한다.

---

## Material 3 easing (cubic-bezier)
- Standard: `cubic-bezier(0.2, 0, 0, 1)`
- Standard Decelerate: `cubic-bezier(0, 0, 0, 1)` (진입에 적합)
- Standard Accelerate: `cubic-bezier(0.3, 0, 1, 1)` (퇴장에 적합)
- Emphasized Decelerate: `cubic-bezier(0.05, 0.7, 0.1, 1)`
- Emphasized Accelerate: `cubic-bezier(0.3, 0, 0.8, 0.15)`
- Linear: `cubic-bezier(0, 0, 1, 1)`
- (M2 standard 곡선) `cubic-bezier(0.4, 0, 0.2, 1)`

## Material 3 duration 토큰 (ms)
- Short: 50 / 100 / 150 / 200 · Medium: 250 / 300 / 350 / 400 · Long: 450 / 500 / 550 / 600 · Extra-long: 700–1000
- 원칙: 영역/이동거리가 커질수록 duration 증가 → 속도 지각 일정.

## NN/G duration 가이드
- 대부분 100–500ms. 단순 피드백 ~100ms. 모달 등 큰 변화 200–300ms. **500ms+ 회피.** 진입 > 퇴장(비대칭).
- 응답은 사용자 액션 후 **0.1초(100ms) 이내** 시작해야 직접 조작감 유지.

## Material 2 시스템 duration 예시 (MUI 등에서 사용, 2차 보조)
- shortest 150 / shorter 200 / short 250 / standard 300 / complex 375 / enteringScreen 225 / leavingScreen 195 (ms).

## Stagger (Motion `stagger()`)
- delay 30–80ms(50ms 전형), 항목 최대 10–15개, 총 ≤800ms. 옵션: `from`("first"/"center"/"last"/index), `startDelay`, `ease`(기본 linear).

## IntersectionObserver (스크롤 리빌)
- `threshold` 0.1–0.3, `rootMargin` 음수(예 `-50px`). 발화 후 `unobserve`/`disconnect`로 정리. scroll 이벤트 핸들러보다 권장.

## 접근성 패턴
- **모달(W3C WAI-ARIA APG dialog)**: `role="dialog"`+`aria-modal="true"`+`aria-labelledby`. focus 이동→trap→Escape→트리거로 반환. **focus 관리·배경 비활성화는 JS 직접 구현**(aria-modal은 동작을 부여하지 않음 — 오표기 시 보조기술 부작용).
- **아코디언/디스클로저**: `aria-expanded` true/false를 펼침 상태와 동기화. grid-template-rows 애니메이션 Chrome 107+.
- **로더**: `role="status"`/`aria-live`/`aria-busy`. count-up 최종값 즉시 접근 가능.
- **prefers-reduced-motion**: CSS `@media (prefers-reduced-motion: reduce)`, JS `matchMedia('(prefers-reduced-motion: reduce)').matches`. 제거보다 완화 권장.

## 성능 (web.dev)
- transform/opacity = 컴포지터 스레드 처리(layout/paint 회피, 60fps). 그 외 속성은 layout/paint 유발.
- `will-change`: 상시 부착 금지, 모션 직전 부착·종료 후 제거. 폴백 `transform:translateZ(0)`.

---

## 라이브러리 버전 주의 (조회일 2026-06-24)

### Framer Motion → **Motion**
- 2025년 리네임: npm `framer-motion` → **`motion`**, import `framer-motion` → **`motion/react`**.
- 조회 시점 최신 메이저로 **v12** 보고(2차 보도 기준). v12: oklch/oklab/색 타입, 하드웨어 가속 스크롤 애니메이션, `layoutAnchor`, 축 고정 layout(`layout="x"/"y"`), `useSpring` `skipInitialAnimation`.
- 구 `framer-motion`도 동작하나 적극 개발 중단. **적용 시 프로젝트가 어느 패키지/버전을 쓰는지 감지해 import 경로를 맞출 것.**
- ⚠️ 정확한 최신 버전은 베이크 신뢰도 한계 → 구현 전 `package.json`의 실제 설치 버전을 따른다.

### Tailwind v3 vs v4
- **빌트인 동일**: `animate-spin`(1s linear), `animate-ping`(1s cubic-bezier(0,0,0.2,1)), `animate-pulse`(2s cubic-bezier(0.4,0,0.6,1)), `animate-bounce`(1s).
- **커스텀 정의 방식 차이**:
  - v3: `tailwind.config.js`의 `theme.extend.animation`/`keyframes`.
  - v4: **CSS-first** — CSS `@theme` 블록에서 `--animate-*` 변수 + `@keyframes`(`--animate-*` → `animate-*` 유틸 생성).
- **v4 신규**: `@starting-style` 기반 `starting:` variant(진입 애니메이션, v3엔 없음), `transition`에 `outline-color` 포함.
- **서드파티**: `tailwindcss-animate`(shadcn/ui) — `animate-in`/`fade-in`/`zoom-in`/`slide-in-from-*` + `animate-out`.
- **적용 시 감지한 Tailwind 메이저 버전에 맞는 정의 방식**을 쓸 것.

---

## Open questions / 베이크 한계
- **21st.dev 개별 컴포넌트 모션 스펙**: 사이트가 JS 렌더링 → 카테고리·개수(carousel 다수, spinner 24, scroll area 26 등)만 확인, 개별 duration/easing/autoplay 미추출.
- **이동 거리(px)**: 1차 표준에 권장값 없음 → 관행값(슬라이드 8–24px, lift 2–6px). "관행" 라벨로 사용.
- **Motion 버전**: v12는 2차 보도 기준 → 구현 시 npm/`package.json` 재확인.

---

## 소스 (조회일 2026-06-24)
- Material 3 easing/duration: m3.material.io/styles/motion/easing-and-duration + github material-components-android `docs/theming/Motion.md`
- Material 2 speed: m2.material.io/design/motion/speed.html
- NN/G: animation-purpose-ux / animation-duration / animation-usability (nngroup.com)
- web.dev: animations-guide / animations-and-performance / prefers-reduced-motion
- MDN: prefers-reduced-motion / Intersection_Observer_API / aria-modal
- W3C WAI-ARIA APG: patterns/dialog-modal
- Tailwind: tailwindcss.com/docs/animation, /docs/upgrade-guide, /blog/tailwindcss-v4
- Motion: motion.dev/docs/stagger, /docs/react-upgrade-guide; npm `framer-motion`/`motion`; github motiondivision/motion
- (2차) PixelFreeStudio 마이크로인터랙션, CSS-Tricks staggering, 아코디언 grid 기법 글
