# ANIMATION_GUIDE — 패턴 카탈로그 + 베이크 모션 토큰

`animation-applier`가 구현의 기준으로, `animation-scout`가 후보 패턴 선택의 기준으로 따르는 가이드다.
값은 1차 표준 소스(Material 3, Nielsen Norman Group, web.dev, MDN, W3C WAI-ARIA, Tailwind/Motion 공식)에서
베이크했다. 출처·버전 상세는 `REFERENCE_SPECS.md` 참조.

> **우선순위**: 사용자가 디자인 시스템/모션 토큰을 제공하면 **그것이 아래 베이크 기본값보다 우선**이다.
> 프로젝트에 기존 토큰(CSS variables·Tailwind theme)이 있으면 재사용을 우선한다.

---

## 베이크 모션 토큰 (기본값)

**Duration 스케일** (NN/G·Material 3 근거)
- 단일 애니메이션은 **100–500ms** 범위. 500ms 이상은 지연으로 느껴져 회피.
- press/토글 등 단순 피드백: **~100ms** (직접 조작감).
- hover/마이크로: **150–200ms**.
- 진입·모달 등 큰 화면 변화: **200–300ms**.
- 비대칭: **진입 > 퇴장** (예: 진입 300ms / 퇴장 200–250ms).
- 영역·이동거리가 클수록 duration을 늘려 속도 지각을 일정하게.
- 무한 모션: 스피너 ~1s, 스켈레톤 shimmer 1.5–2s.

**Easing** (용처별)
- 진입: **ease-out** (빠르게 시작→감속). CSS `ease-out` 또는 Material Standard Decelerate `cubic-bezier(0,0,0,1)`.
- 퇴장: **ease-in** (가속하며 떠남).
- 위치 전환: **ease-in-out** / Material Standard `cubic-bezier(0.2,0,0,1)` (M2: `cubic-bezier(0.4,0,0.2,1)`).
- **linear 회피**(부자연스러움) — 단, 무한 회전 스피너는 linear가 적합.
- spring: drag·토글·hover 등 물리감이 필요한 인터랙티브 요소(Motion 기본 지원).

**이동 거리** (실무 관행 — 1차 px 권장값은 표준에 없음)
- 진입 슬라이드: **8–24px**. hover lift: **2–6px**. 큰 패닝/스케일은 vestibular 위험 → 절제.

**Stagger**
- 항목 간 delay **30–80ms(50ms 전형)**, 총 시퀀스 **≤ ~800ms**, 항목 **최대 10–15개**.

**불변 규칙**: 모든 모션은 `transform`/`opacity`만, 그리고 `prefers-reduced-motion` 폴백 필수(아래 §접근성).

---

## 패턴 카탈로그

각 패턴: 언제 / 권장 토큰 / 성능 / 접근성 / 구현 스케치(CSS + Motion).

### 진입 (fade-in / slide-up)
- **언제**: 첫 로드 콘텐츠 등장, 페이지 전환, 카드/섹션 진입(첫인상).
- **토큰**: 200–300ms, ease-out, `translateY` 8–24px + opacity.
- **성능**: `opacity` + `transform: translateY()`만. `top`/`margin` 금지.
- **접근성**: reduced-motion에서 이동 제거, opacity만 또는 즉시 표시.
- **CSS**: `@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}` → `animation:fadeUp 240ms ease-out both`.
- **Motion**: `initial={{opacity:0,y:16}} animate={{opacity:1,y:0}} transition={{duration:0.24,ease:"easeOut"}}` (import `motion/react`).

### Stagger 리스트
- **언제**: 리스트·카드 그리드·메뉴·검색 결과가 함께 진입할 때 순차 등장으로 흐름 전달.
- **토큰**: delay 30–80ms, **최대 10–15개**, 총 ≤800ms. 초기 전체 로드 일괄 stagger 지양 — 스크롤 진입분만.
- **성능**: 긴 리스트 전체 stagger는 레이어/리플로우 비용 큼 → IntersectionObserver로 뷰포트 진입분만.
- **접근성**: reduced-motion에서 stagger 제거, 일괄 표시.
- **CSS**: 항목 `animation-delay: calc(var(--i) * 50ms)`.
- **Motion**: `animate(els,{opacity:1},{delay:stagger(0.05)})` — `from`/`startDelay` 옵션.

### 스크롤 리빌 (IntersectionObserver)
- **언제**: 스크롤로 섹션·이미지·콘텐츠 등장.
- **토큰**: `threshold` 0.1–0.3, `rootMargin` 음수(예 `-50px`)로 중앙 근처 진입 시 발화. 발화 후 `unobserve`.
- **성능**: scroll 이벤트 핸들러 대신 **IntersectionObserver**(비동기·메인스레드 부담 적음).
- **접근성**: reduced-motion에서 reveal 비활성(즉시 표시).
- **Motion**: `whileInView={{opacity:1,y:0}} viewport={{once:true, margin:"-50px"}}`.

### Hover lift / scale
- **언제**: 클릭 가능한 카드·버튼의 인터랙티브 signifier.
- **토큰**: 150–200ms, ease-out, `translateY(-2~-6px)` + `scale(1.02~1.05)`.
- **성능**: transform 위주. `box-shadow`는 paint 유발 → 가능하면 그림자 pseudo-element의 opacity로 대체.
- **접근성**: hover는 터치/키보드에 없음 → 핵심 정보를 hover에만 의존 금지. **`:focus-visible`에도 동일 피드백**.
- **CSS**: `.card{transition:transform 180ms ease-out} .card:hover,.card:focus-visible{transform:translateY(-4px) scale(1.02)}`.
- **Motion**: `whileHover={{y:-4,scale:1.02}}`.

### Press(active) 피드백
- **언제**: 버튼/탭 누름 즉각 확인.
- **토큰**: ~100ms, `scale(0.96~0.98)`. 응답은 액션 후 **0.1초 이내** 시작.
- **접근성**: `:active` + `:focus-visible` 둘 다. 매우 짧아 reduced-motion에서도 유지 안전.
- **CSS**: `button:active{transform:scale(0.97)} button{transition:transform 100ms ease-out}`.
- **Motion**: `whileTap={{scale:0.97}}`.

### 모달 · 드로어 트랜지션
- **언제**: 오버레이 다이얼로그, 사이드 드로어.
- **토큰**: 진입 200–300ms ease-out / 퇴장 200–250ms ease-in. 모달 fade+scale(0.95→1)+백드롭 dim, 드로어 `translateX/Y` 슬라이드.
- **성능**: transform/opacity, 백드롭 opacity.
- **접근성(중요)**: 열림 시 모달로 focus 이동 → 닫힐 때까지 **focus trap** → Escape 닫기 → 닫으면 트리거로 focus 반환. `role="dialog"`+`aria-modal="true"`+`aria-labelledby`. **focus 관리·배경 비활성화는 JS로 직접 구현**(aria-modal이 동작을 만들지 않음). 큰 스케일/패닝은 reduced-motion에서 fade만.
- **Motion**: `AnimatePresence` + `initial/animate/exit`.

### 아코디언 expand / collapse
- **언제**: FAQ, 설정 그룹, 콘텐츠 접기.
- **토큰**: ~300ms ease-in-out. height auto 직접 애니메이트 불가 → **CSS Grid `grid-template-rows: 0fr → 1fr`**(고정 max-height·JS 측정 불필요), 내부 div `overflow:hidden`.
- **성능**: grid-template-rows는 layout을 건드림(transform보다 비쌈). 항목 많으면 주의.
- **접근성**: 토글 버튼 **`aria-expanded`를 펼침 상태와 동기화**. (Chrome 107+ grid-template-rows 애니메이션 지원.)
- **CSS**: `.panel{display:grid;grid-template-rows:0fr;transition:grid-template-rows 300ms ease}.panel.open{grid-template-rows:1fr}`.
- **Motion**: `animate={{height:isOpen?"auto":0}}`.

### 캐러셀
- **언제**: 이미지/콘텐츠 쇼케이스, 테스티모니얼.
- **토큰**: 슬라이드 전환 300–500ms ease-in-out, transform `translateX`.
- **성능**: transform 트랙 이동, 슬라이드 lazy-load.
- **접근성**: 자동재생은 reduced-motion에서 정지 + **정지 버튼 제공(WCAG)**, 키보드 화살표, 현재 슬라이드 aria.

### 스켈레톤 / 스피너 로더
- **언제**: 200ms 이상 지연 시 "준비 안 됨" 상태 신호.
- **토큰**: 스켈레톤 shimmer 1.5–2s 무한, 스피너 회전 ~1s **linear**. (Tailwind 빌트인: `animate-spin`=1s linear, `animate-pulse`=2s, `animate-ping`=1s.)
- **성능**: transform(rotate)+opacity만(무한 모션은 컴포지터 전용 속성 엄수).
- **접근성**: `role="status"`/`aria-live`/`aria-busy`. reduced-motion에서 빠른 회전은 opacity 펄스로 완화 가능.

### Count-up 숫자
- **언제**: 대시보드 KPI·통계 강조.
- **토큰**: 1–2s ease-out. 너무 길면 지연감.
- **성능**: 텍스트 갱신은 layout/paint 유발 → rAF로 갱신, 과도 빈도 지양.
- **접근성**: **최종값은 즉시 접근 가능**(스크린리더). reduced-motion에서 최종값 즉시 표시.
- **Motion**: `useMotionValue` + `animate(count,target,{duration})` + `useTransform`.

### 패럴랙스 (절제)
- **언제**: 히어로 깊이감. 장식적 위험 큼 → 절제.
- **토큰**: 작은 이동(배경 < 전경), 미묘하게.
- **성능**: CSS scroll-driven animations / IntersectionObserver(메인스레드 scroll 핸들러 회피).
- **접근성(중요)**: 큰 객체 스케일/패닝은 대표 vestibular 트리거 → **reduced-motion에서 반드시 비활성**.

---

## 접근성 — `prefers-reduced-motion` (모든 패턴 공통, 필수)

**CSS**
```css
@media (prefers-reduced-motion: reduce) { /* 이동 제거, duration 단축/제거, opacity만 */ }
```
**JS**
```js
const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
if (mq.matches) { /* 모션 비활성/완화 */ }
mq.addEventListener('change', cb);
```
- 권장은 **제거가 아니라 완화/대체** — opacity fade·짧은 duration은 안전. `animation:none !important`는 애니메이션 이벤트(`animationend`)에 의존하는 코드를 깨뜨릴 수 있으니, 필요 시 duration을 인지 불가 수준(예: 0.01ms)으로 단축.
- vestibular 트리거(스케일/큰 패닝)는 reduced-motion에서 반드시 제거.
- content shift 방지: 레이아웃을 흔드는 애니메이션 회피(transform 사용), 진입 공간은 스켈레톤으로 예약.

## 성능 — 불변 규칙 (모든 패턴 공통)
- **transform/opacity만 애니메이트**(컴포지터 스레드 → 60fps). `top/left/width/height/margin/padding` 금지.
- 위치=`translate()`, 크기=`scale()`. `box-shadow`/`background` 등은 paint 유발 → 절제.
- `will-change` 남용 금지: 상시 부착 금지, 자주 변하는 요소에 모션 직전 부착 → 종료 후 제거(폴백 `transform:translateZ(0)`).
- 긴 리스트는 IntersectionObserver로 뷰포트 진입분만.
