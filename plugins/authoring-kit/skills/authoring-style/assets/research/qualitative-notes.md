# 정성 문체 요소 분류 체계 — 리서치 노트

> 목적: 사용자가 관리하는 자유 서술형 문체 지시문(directive)을 **전문 이론에 근거한 정성적 문체 요소 분류**에 귀속시키고, 품질 게이트의 LLM 심사관이 **읽기만으로** 판정할 수 있게 하는 것.
> 전제: voice 층의 4축 = `register`(어조·격식·입장) / `rhythm`(호흡·길이 분포·전개 완급) / `device`(독자 관여 장치·수사·예시·도입/마무리) / `lexicon`(어휘 선택 경향).
> 타 층 소유: `structure`(문서 유형별 섹션과 순서) / `evidence`(사실 정확성) / `grammar`(번역투·부자연한 한국어) / `comprehension`(점진적 공개·용어 정의).
>
> **검증 방법 메모**: 이 세션에서는 WebFetch가 egress 프록시에 막혀(uv.es, eric.ed.gov, wikipedia, encykorea, hangeul.go.kr 등 전부 EGRESS_BLOCKED) 원문 페이지를 직접 열지 못했다. 아래 "검증됨"은 **WebSearch 결과 스니펫으로 확인한 것**, "[미검증]"은 기억·2차 지식에 의존한 것이다.

---

## 0. 설계 결론 요약

1. **2층 구조, 9개 상위 범주 / 40개 말단 요소.** 상위 범주마다 voice 축이 정확히 하나: register ← `tenor`·`stance` / rhythm ← `cadence`·`pacing` / device ← `figure`·`engage`·`illus`·`frame` / lexicon ← `diction`.
2. **축 배정 규칙(충돌 시 판정 기준)**
   - *누구에게 어떤 태도로 말하는가* → register. *문장·단락이 어떤 속도와 호흡으로 흐르는가* → rhythm. *독자를 붙잡기 위해 어떤 장치를 쓰는가(단어를 넘어선 구성 단위)* → device. *어떤 단어를 고르는가(단어 단위 선택)* → lexicon.
   - 수식어·미사여구의 양(건조체↔화려체)은 **단어 단위 선택**이므로 lexicon. 은유·대구 같은 **비유·배열 구조**는 device.
   - 문장 길이(간결체↔만연체)는 rhythm. 군더더기 삭제(Omit needless words)는 **단어 경제**이므로 lexicon. 둘은 독립적이다. 짧은 문장에도 군더더기가 있을 수 있다.
   - 강건체↔우유체는 Appraisal의 Graduation(Force)과 대응하므로 register(`stance.force`).
3. **정성 요소와 정량 요소 분리.** 평균 문장 길이, 종결어미 비율, 금지어 등장 횟수는 스크립트로 셀 수 있으므로 이 분류에 넣지 않는다. 이 분류의 말단 요소는 **"그 수치가 이 글의 목적·독자·장르에 맞는가"**라는, 읽어야만 판단할 수 있는 적합성 질문만 다룬다.
4. **말단 요소는 대부분 "스펙트럼(양극)"이다.** 지시문은 보통 한쪽 극으로 기울이라거나 범위 안에 머물라고 요구한다. 극 자체는 좋고 나쁨이 아니다. 심사관은 **지시문이 지정한 위치와 실제 위치의 거리**를 판정한다.
5. **한국어 특수성 반영.** (a) 상대높임법(종결 문체)은 독립 요소다. Kim & Biber(1994)의 한국어 다차원 분석에서도 'honorification'이 별도 차원으로 나왔다. (b) 한국어는 서술어가 문장 끝에 오므로(SOV) 영어의 end-focus·periodic sentence는 그대로 옮기지 않고 **'긴 관형절 앞머리 부담' 대 '연결어미로 이어 붙이기'**로 재해석했다(`cadence.shape`). (c) 이태준의 3대 대립(간결↔만연, 강건↔우유, 건조↔화려)은 각각 rhythm·register·lexicon에 하나씩 배치했다.

---

## 1. 분류 트리 한눈에 보기

```
register
├─ tenor  격식·관계 (Halliday tenor/mode, Joos, 상대높임법)
│   ├─ tenor.formality        격식도            격식 ↔ 비격식
│   ├─ tenor.speech-level     종결 문체(높임 등급) 합쇼체 / 해요체 / 해라체(-다)
│   ├─ tenor.orality          구어성            구어체 ↔ 문어체
│   ├─ tenor.distance         독자와의 거리·위계   권위적·교시적 ↔ 대등·동료적
│   └─ tenor.key              진지도            엄숙 ↔ 경쾌·유머
└─ stance  입장·평가 (Hyland stance, Martin & White Appraisal)
    ├─ stance.certainty       확신도 조율        유보(hedge) ↔ 단정(booster)
    ├─ stance.attitude        평가·감정 표출      절제·중립 ↔ 표출·평가적
    ├─ stance.presence        저자 현존          비인칭·익명 ↔ 1인칭 드러냄
    ├─ stance.dialogism       이견 다루기         단성적(단언) ↔ 다성적(양보·인정)
    └─ stance.force           어세              강건체 ↔ 우유체
rhythm
├─ cadence  문장 호흡 (이태준, Provost, Leech & Short, Quirk, Williams)
│   ├─ cadence.length         문장 호흡 길이      간결체 ↔ 만연체
│   ├─ cadence.variation      길이·구조 변주      균일 ↔ 변주
│   ├─ cadence.shape          문장 형상          앞머리 적재형 ↔ 뒤로 잇기형
│   ├─ cadence.emphasis       강조 위치          (배치 원칙: 핵심을 끝/앞에)
│   └─ cadence.sound          소리 흐름          (낭독 시 걸림·단조 어미 반복)
└─ pacing  전개 완급 (Biber, Clark, 6+1 Sentence Fluency)
    ├─ pacing.density         정보 밀도          압축 ↔ 완만
    ├─ pacing.paragraph       단락 호흡          짧은 단락 ↔ 긴 단락, 변주
    ├─ pacing.zoom            상술↔개괄 비율      장면·세부 ↔ 요약·개괄
    └─ pacing.momentum        전진감·여담 허용     직진 ↔ 우회·여담
device
├─ figure  수사 문채 (Leech & Short figures, Silva Rhetoricae, 수사법 3분류)
│   ├─ figure.imagery         비유(tropes of likeness) 은유·직유·의인·유추
│   ├─ figure.scheme          배열 문채           대구·대조·반복·점층·도치
│   └─ figure.indirection     간접 표현           반어·역설·완서·과장
├─ engage  독자 관여 (Hyland engagement markers)
│   ├─ engage.address         독자 호명·포함       '여러분/당신/우리'
│   ├─ engage.question        질문              수사의문·설의·실질 질문
│   ├─ engage.directive       지시·권유           명령·청유·당위
│   ├─ engage.shared-ground   공유 기반 호소       '누구나 ~한 적 있다'
│   └─ engage.aside           여담·괄호 논평       괄호·줄표 속 저자 목소리
├─ illus  예시·사례 (Hayakawa, Clark, Strunk)
│   ├─ illus.example          예시 운용(추상 사다리) 원리 선행 ↔ 예시 선행
│   ├─ illus.anecdote         일화·장면 서사       사례 서사 사용 여부·비중
│   └─ illus.analogy          설명적 유추          낯선 것을 익숙한 것에 빗대기
└─ frame  도입·마무리 (hook/closing 유형론)
    ├─ frame.opening          도입 방식           직입 ↔ 후킹(일화·질문·장면·수치·역설)
    └─ frame.closing          마무리 방식          요약 / 수미상관 / 함의·전망 / 행동 촉구 / 여운
lexicon
└─ diction  어휘 선택 (Leech & Short lexical, Strunk & White, Williams, 박갑수, 국립국어원)
    ├─ diction.origin         어종              고유어 ↔ 한자어 ↔ 외래어
    ├─ diction.concreteness   구체성            추상 ↔ 구체
    ├─ diction.precision      정밀성            뭉뚱그린 말 ↔ 딱 맞는 말
    ├─ diction.technicality   전문성 수준         일상어 ↔ 전문어
    ├─ diction.ornament       수식 밀도          건조체 ↔ 화려체
    ├─ diction.economy        어휘 경제          군더더기 ↔ 절약
    ├─ diction.freshness      신선도            상투어·상용구 ↔ 참신한 표현
    ├─ diction.action         행위 중심성         명사화·정태적 ↔ 동사·행위자 중심
    └─ diction.repetition     반복↔바꿔 쓰기       동어 반복 유지 ↔ 우아한 변이(elegant variation)
```

범주별 말단 수: tenor 5 / stance 5 / cadence 5 / pacing 4 / figure 3 / engage 5 / illus 3 / frame 2 / diction 9 = **41**. (`illus.analogy`는 `figure.imagery`에 합쳐 40개로 줄여도 된다. 5절 참고)

---

## 2. 말단 요소 상세

항목 형식: 정의 / 스펙트럼 / 심사 질문(LLM judge가 읽으며 묻는 것) / 지시문 예 / 축 / 근거 / 경계.

### 2.1 `tenor` — 격식·관계 (축: register)

Halliday의 tenor(참여자 관계: 지위, 친밀도, 감정 관여)와 mode(채널: 구어/문어)를 문체 선택으로 옮긴 범주. field(주제)는 문체가 아니라 내용이므로 제외한다.

#### `tenor.formality` 격식도 — Formality level
- 정의: 글이 상정하는 사회적 상황의 공식성 정도. 어휘·종결·문장 구성 전반에 드러나는 "차려입은 정도".
- 스펙트럼: 의례적(frozen) · 격식(formal) · 상담적(consultative) · 일상(casual) · 친밀(intimate). Joos의 5단계를 글쓰기에서는 보통 formal~casual 3단으로 쓴다.
- 심사 질문: ① 문서 유형과 독자에 비해 너무 딱딱하거나 너무 풀어졌는가? ② 격식 수준이 글 전체에서 흔들리지 않는가(갑작스러운 격하·격상)? ③ 흔들림이 있다면 의도된 효과(인용, 강조)인가?
- 지시문 예: "격식은 {상담적} 수준으로 유지하되 속어·유행어는 쓰지 않는다." / "공문 수준의 의례적 표현은 피한다."
- 근거: Joos, *The Five Clocks* (1962) 5단계; Halliday tenor.
- 경계: 종결어미 등급 자체는 `tenor.speech-level`, 구어 특유 어휘는 `tenor.orality`에서 다룬다.

#### `tenor.speech-level` 종결 문체(상대높임 등급) — Speech level / honorific ending
- 정의: 문장 종결에 쓰는 상대높임 등급의 선택과 그 적합성. 격식체(하십시오체·해라체)와 비격식체(해요체·해체).
- 스펙트럼: 합쇼체(-ㅂ니다) / 해요체(-요) / 해라체·평서 '-다'(문어 기본값) / 해체(반말).
- 심사 질문: ① 선택한 등급이 독자와 매체에 맞는가(블로그, 매뉴얼, 논설 등)? ② 등급 전환이 있다면 인용이나 대화 같은 정당한 이유가 있는가? ③ 등급과 어휘 격식이 어긋나지 않는가(해요체에 딱딱한 한자어가 몰리는 경우 등)?
- 지시문 예: "본문은 '-다' 평서체, 독자에게 직접 말을 거는 박스만 해요체." / "합쇼체를 쓰되 '-하시기 바랍니다'류의 공문투 종결은 줄인다."
- 근거: 한국어 상대높임법 체계(격식체 4등급, 비격식체 2등급); 문어는 대개 해라체 하나로 단순화되는 경향(국립국어원 온라인가나다 계열 설명); Kim & Biber(1994)에서 honorification이 한국어 사용역의 독립 차원으로 나옴.
- 경계: **종결어미 일관성 검사(비율 계산)는 스크립트 몫**이다. 이 요소는 선택의 적합성과 전환의 정당성만 판정한다.

#### `tenor.orality` 구어성 — Spoken vs written mode
- 정의: 말하듯 쓰는가, 글답게 쓰는가. 축약('거', '근데'), 담화표지('뭐', '그러니까'), 감탄, 생략이 얼마나 허용되는가.
- 스펙트럼: 구어체 ↔ 문어체.
- 심사 질문: ① 구어 요소(축약, 담화표지, 말줄임)가 지시된 수준만큼 있거나 없는가? ② 구어체를 쓸 때 문장이 실제로 말처럼 들리는가, 아니면 문어 문장에 구어 어미만 붙였는가? ③ 문어체를 쓸 때 대화체 표지가 새어 들어오지 않는가?
- 지시문 예: "강연 원고처럼 말하는 문체로 쓰되 '뭐', '약간' 같은 군말은 넣지 않는다." / "'거'가 아니라 '것'을 쓴다."
- 근거: Halliday mode; Biber Dimension 1(Involved ↔ Informational; 축약·담화 불변화사·1·2인칭 대명사가 involved 쪽 특징); 국립국어원 구어/문어 구분 답변('거'→'것', 해요체→하십시오체).
- 경계: 격식과 구어성은 독립적이다. 격식 있는 구어(연설)도 있고 비격식 문어(메모)도 있다.

#### `tenor.distance` 독자와의 거리·위계 — Social distance & authority
- 정의: 필자가 독자보다 위(가르침), 옆(동료), 아래(봉사) 중 어디에 서는가. 권위적·훈계조 표현을 얼마나 쓰는가.
- 스펙트럼: 권위적·교시적 ↔ 대등·동료적 ↔ 겸양·봉사적.
- 심사 질문: ① '~해야 한다', '당연히', '명심하라' 같은 위계 표지가 독자를 낮추는가? ② 독자의 지식과 판단을 존중하는가, 가르치려 드는가? ③ 지나친 겸양('부족하지만', '감히')이 신뢰를 깎지 않는가?
- 지시문 예: "독자를 같은 분야 동료로 대하고, 훈계하는 투는 쓰지 않는다." / "'~하도록 한다', '~할 것' 같은 지시형 공문투는 쓰지 않는다."
- 근거: Halliday tenor(지위·권력 관계); 국립국어원 공공언어 진단 기준 중 '권위적·차별적 표현' 항목.
- 경계: 명령·청유 **장치**의 빈도와 기능은 `engage.directive`, 여기서는 그것이 만들어 내는 **관계의 느낌**만 판정한다.

#### `tenor.key` 진지도 — Key (gravity ↔ levity)
- 정의: 글의 전반적 기분이 엄숙한가, 담담한가, 경쾌한가, 장난스러운가. 유머 허용 수준.
- 스펙트럼: 엄숙 ↔ 담담 ↔ 경쾌 ↔ 유희.
- 심사 질문: ① 주제의 무게(사고, 손실, 건강)에 비해 가볍거나 무겁지 않은가? ② 유머가 있다면 독자를 겨냥하지 않고 논지를 흐리지 않는가? ③ 기분이 글 중간에 설명 없이 바뀌지 않는가?
- 지시문 예: "가벼운 위트는 허용하되 단락당 한 번을 넘기지 않는다." / "장애 관련 주제에서는 농담을 쓰지 않는다."
- 근거: [미검증] Hymes SPEAKING 모델의 'Key'(tone/manner). Leech & Short Context 항목의 '필자의 태도(tone)'.
- 경계: 반어·풍자 같은 **기법**은 `figure.indirection`.

### 2.2 `stance` — 입장·평가 (축: register)

Hyland(2005) 상호작용 메타담화의 stance 쪽(hedges, boosters, attitude markers, self-mention)과 Martin & White(2005) Appraisal의 Attitude·Engagement·Graduation을 합친 범주.

#### `stance.certainty` 확신도 조율 — Epistemic calibration
- 정의: 명제에 싣는 확신의 강도를 근거 수준에 맞추는 일.
- 스펙트럼: 유보(hedge: '~일 수 있다', '아마', '~로 보인다') ↔ 단정(booster: '분명히', '반드시', '~임에 틀림없다').
- 심사 질문: ① 글 안에 제시된 근거가 약한 주장에 단정 표현을 쓰지 않았는가? ② 확립된 사실에 불필요한 유보를 덧대 흐리지 않았는가(과잉 hedging)? ③ 한 문장에 유보를 겹겹이 쌓지 않았는가('~일 수도 있을 것으로 보인다')?
- 지시문 예: "확신도는 근거 수준에 맞춘다." / "추정에는 '~로 보인다'를 쓰고 한 문장에 유보 표현은 하나만 쓴다."
- 근거: Hyland 2005 hedges/boosters; Martin & White Engagement의 entertain(확장) ↔ pronounce(축소).
- 경계: **근거가 참인지는 evidence 층**이 판정한다. 여기서는 "글이 스스로 제시한 근거"에 비춰 언어적 확신도가 맞는지만 본다.

#### `stance.attitude` 평가·감정 표출 — Attitude
- 정의: 필자가 대상에 대해 감정(affect), 윤리적 평가(judgement), 미적·가치 평가(appreciation)를 얼마나 드러내는가.
- 스펙트럼: 절제·중립 ↔ 평가적·정서적.
- 심사 질문: ① '놀랍게도', '안타깝게도', '훌륭한' 같은 평가어가 지시된 수준을 넘거나 모자라지 않는가? ② 평가가 근거 뒤에 오는가, 근거를 대신하는가? ③ 감정 표현이 독자의 판단을 대신 내려 주지 않는가?
- 지시문 예: "형용사로 평가하지 말고 사실을 보여 준 뒤 판단은 독자에게 맡긴다." / "제품 리뷰에서는 장단점 평가를 분명히 드러낸다."
- 근거: Martin & White Attitude(affect / judgement / appreciation, 각각 긍정↔부정 연속체); Hyland attitude markers.
- 경계: 과장된 수식어 **어휘**의 밀도는 `diction.ornament`, 강도 조절은 `stance.force`.

#### `stance.presence` 저자 현존 — Authorial self-mention
- 정의: 필자가 '나/저/필자/우리(배타적)'로 글에 등장하는 정도.
- 스펙트럼: 비인칭·익명(행위자 숨김) ↔ 1인칭 전면화.
- 심사 질문: ① 1인칭 사용이 지시(허용·금지·빈도 느낌)에 맞는가? ② 1인칭이 경험과 판단의 책임 주체를 밝히는 데 쓰이는가, 자기 과시에 쓰이는가? ③ 비인칭을 택했을 때 책임 소재가 흐려지지 않는가('~라고 여겨진다')?
- 지시문 예: "개인 경험은 1인칭으로 쓰되 주장 문장에서는 '나는 ~라고 생각한다'를 쓰지 않는다." / "'필자는'이라는 표현은 쓰지 않는다."
- 근거: Hyland 2005 self-mention.
- 경계: 독자를 '우리'로 끌어들이는 포괄적 '우리'는 `engage.address`.

#### `stance.dialogism` 이견 다루기 — Dialogic positioning
- 정의: 다른 목소리와 반대 입장을 글에 들여 인정·양보·반박하는가, 한 목소리로 단언하는가.
- 스펙트럼: 단성적(monogloss, 대안 차단) ↔ 다성적(heterogloss: 인정 acknowledge, 거리두기 distance, 양보 후 반박 counter).
- 심사 질문: ① 논쟁적 주장에서 유력한 반론을 인정하는가? ② 인용한 타인의 견해와 필자 견해의 경계가 분명한가(동의하는지, 거리를 두는지)? ③ '물론 ~지만'식 양보가 형식에 그치지 않는가(허수아비)?
- 지시문 예: "주요 주장마다 가장 강한 반론을 한 문장으로 인정한 뒤 답한다." / "업계 통념을 인용할 때는 동의하지 않는다는 거리를 표시한다."
- 근거: Martin & White Engagement: contract(disclaim: deny/counter, proclaim: concur/pronounce/endorse) ↔ expand(entertain, attribute: acknowledge/distance).
- 경계: 반론 **섹션**을 둘지는 structure. 인용 출처의 정확성은 evidence.

#### `stance.force` 어세 — Force (강건체 ↔ 우유체)
- 정의: 표현의 힘과 부드러움. 단호하고 힘찬가, 온화하고 부드러운가. 강조어(intensifier)와 완화어(downtoner)의 전반적 기울기.
- 스펙트럼: 강건체(剛健體: 힘차고 호소력 있음) ↔ 우유체(優柔體: 부드럽고 우아함).
- 심사 질문: ① 전체 어세가 지시된 쪽으로 기울어 있는가? ② 강건체라면 공격적이거나 선동적으로 넘어가지 않는가? ③ 우유체라면 무르거나 모호해 요점이 흐려지지 않는가?
- 지시문 예: "결론 단락은 단호하게 쓰되 느낌표는 쓰지 않는다." / "위로 편지이므로 부드럽고 온화한 어세를 유지한다."
- 근거: 이태준 『문장강화』 문체론의 강건체↔우유체(표현이 강한가, 약하고 부드러운가); Martin & White Graduation–Force(세기 올림·내림).
- 경계: 확신(인식적)은 `stance.certainty`. 이 요소는 정서적·수사적 세기다. "확실하지만 부드럽게"도 가능하다.

### 2.3 `cadence` — 문장 호흡 (축: rhythm)

#### `cadence.length` 문장 호흡 길이 — Sentence breath (간결체 ↔ 만연체)
- 정의: 한 문장에 담는 절(생각 단위)의 수와 그로 인한 호흡의 길이.
- 스펙트럼: 간결체(簡潔體: 압축하고 함축함) ↔ 만연체(蔓衍體: 길게 이어 풀어냄).
- 심사 질문: ① 문장 호흡이 지시된 쪽에 있는가? ② 간결체라면 뚝뚝 끊겨 논리 연결이 사라지지 않았는가(접속 관계가 증발)? ③ 만연체라면 한 문장 안에서 주어와 서술어 호응이 멀어져 숨이 차지 않는가?
- 지시문 예: "한 문장에는 생각 하나만 담는다." / "서정적 대목에서는 긴 호흡을 허용하되 한 문장에 연결어미는 세 번까지."
- 근거: 이태준 『문장강화』 제8강 '문체에 대하여'(간결체↔만연체: 구절의 길고 짧음); Strunk & White "vigorous writing is concise"; Federal Plain Language Guidelines "write short sentences".
- 경계: **평균·최대 길이 계산은 스크립트 몫**. 이 요소는 호흡이 내용에 맞는지를 판정한다(복잡한 인과는 긴 문장이 더 명료할 때도 있다: Clark "Fear not the long sentence").

#### `cadence.variation` 길이·구조 변주 — Variation
- 정의: 문장 길이와 구문 유형(단문·복문, 평서·의문)을 섞어 단조로움을 피하는 정도.
- 스펙트럼: 균일(메트로놈) ↔ 변주(음악).
- 심사 질문: ① 같은 길이·같은 틀의 문장이 연달아 나와 단조롭지 않은가? ② 짧은 문장이 강조 지점(전환, 결론)에 배치되어 효과를 내는가? ③ 변주가 기계적 교대(짧-길-짧-길)로 흐르지 않는가?
- 지시문 예: "긴 설명 문장 뒤에는 짧은 문장으로 요점을 박는다." / "같은 구조의 문장을 세 번 넘게 잇지 않는다(의도적 대구는 예외)."
- 근거: Gary Provost, *100 Ways to Improve Your Writing* "This sentence has five words… I vary the sentence length, and I create music"; Roy Peter Clark *Writing Tools* "Set the pace with sentence length"; 6+1 Trait 'Sentence Fluency'.
- 경계: 의도적 대구·반복은 `figure.scheme`.

#### `cadence.shape` 문장 형상 — Sentence shape (anticipatory ↔ trailing)
- 정의: 정보가 문장의 어느 쪽에 쌓이는가. 한국어에서는 ① 긴 관형절·부사절이 주어 앞에 쌓이는 **앞머리 적재형**(영어 periodic/anticipatory에 해당), ② 주절 뒤로 연결어미(-고, -며, -는데, -어서)를 계속 잇는 **뒤로 잇기형**(loose/cumulative에 해당, 과하면 sprawl)이 있다.
- 스펙트럼: 앞머리 적재 ↔ 균형 ↔ 뒤로 잇기.
- 심사 질문: ① 핵심 명사 앞에 수식이 너무 길어 독자가 누가 무엇인지를 기다리게 되지 않는가? ② 연결어미 사슬이 길어 문장이 논리 없이 늘어지지 않는가? ③ 긴 문장이라도 뒤에 붙는 수식(요약·재진술 수식)으로 읽기 쉬운 형태를 갖추었는가?
- 지시문 예: "주어 앞에 관형절을 두 겹 넘게 쌓지 않는다." / "'-는데'로 문장을 잇지 말고 끊어서 관계를 드러낸다."
- 근거: Leech & Short 문법 범주의 "anticipatory structure(주절 주어 앞의 종속절, 동사 앞의 복잡한 주어)" 대 trailing 구조(검색 스니펫으로 확인); periodic ↔ loose/cumulative 문장(수사학 일반); Williams *Style* 'Shape'(sprawl 통제, resumptive·summative·free modifier).
- 경계: 주술 호응 오류, 비문은 grammar.

#### `cadence.emphasis` 강조 위치 — Emphatic placement (end-focus)
- 정의: 문장과 단락에서 가장 무거운 정보를 어디에 두어 힘을 싣는가.
- 스펙트럼: (양극이 아니라 배치 원칙) 끝 강조 / 앞 강조 / 분산.
- 심사 질문: ① 문장의 핵심어가 강세 자리에 오는가? 한국어는 서술어가 끝에 고정되므로 서술어 직전 자리, 주제어 '-은/는' 자리, 분열문('~한 것은 ~이다')을 본다. ② 단락의 마지막 문장이 힘 있는 문장인가, 사족으로 끝나는가? ③ 강조 장치(도치, 분열문)를 남발해 강조가 무뎌지지 않았는가?
- 지시문 예: "단락은 가장 중요한 문장으로 끝낸다. 부연으로 끝내지 않는다." / "'~한 것은 ~이다' 강조 구문은 글 전체에서 세 번까지만 쓴다."
- 근거: Quirk et al. end-focus(초점은 절 끝 내용어에)·end-weight(무거운 요소를 뒤로); Williams stress position("End sentences with information that is new, complex, and important"); Strunk & White "Place the emphatic words of a sentence at the end"(검색 결과에서 원문 확인은 못 함, [부분검증]); Clark "Order words for emphasis. Place strong words at the beginning and at the end."
- 경계: 구정보→신정보 흐름과 주제 연쇄(topic strings)는 **이해 가능성**의 문제이므로 comprehension. 여기서는 수사적 힘의 배치만 본다.

#### `cadence.sound` 소리 흐름 — Euphony & sound patterning
- 정의: 소리 내어 읽을 때의 흐름. 같은 종결어미의 단조 반복(-다. -다. -다.), 같은 조사·어미의 중첩('-의 -의 -의', '-고 -고'), 두운·각운 같은 음운 패턴.
- 스펙트럼: 걸림·단조 ↔ 매끄러움 ↔ (의도적) 운율.
- 심사 질문: ① 낭독하면 혀가 걸리는 음절 중첩이나 조사 연쇄가 있는가? ② 문장 끝 소리가 단조롭게 반복되어 졸리지 않는가? ③ 의도한 운율이 있다면 과하지 않은가?
- 지시문 예: "소리 내어 읽었을 때 걸리는 문장은 고친다." / "'-었다'로 끝나는 문장을 네 번 넘게 잇지 않는다."
- 근거: Leech & Short Figures of speech – phonological schemes(각운·두운·유운, 리듬 패턴); 6+1 Trait Sentence Fluency("the way in which the writing plays to the ear").
- 경계: 종결어미 연속 횟수는 셀 수 있다. **셀 수 있는 부분은 스크립트로 넘기고**, 이 요소는 청각적 인상만 판정한다.

### 2.4 `pacing` — 전개 완급 (축: rhythm)

#### `pacing.density` 정보 밀도 — Information density
- 정의: 문장·단락당 새 개념과 사실이 얼마나 빽빽한가. 독자가 한 번에 소화할 양을 두고 고르는 속도.
- 스펙트럼: 압축(명사구 적층, 전문가용) ↔ 완만(풀어 쓰기, 입문자용).
- 심사 질문: ① 한 문장에 새 개념이 여럿 몰려 과부하가 걸리지 않는가? ② 반대로 이미 한 말을 되풀이해 늘어지지 않는가? ③ 밀도가 독자 수준(지시문이 정한 독자)에 맞는가?
- 지시문 예: "한 문장에 새 개념은 하나만 도입한다." / "전문가용 요약이므로 부연 없이 밀도 높게 쓴다."
- 근거: Biber Dimension 1 informational 극(명사, 전치사구, 한정 형용사가 쌓인 정보 밀도); 이태준 간결체의 '압축·함축'.
- 경계: 개념을 정의하는 순서와 방식(점진적 공개)은 comprehension. 여기서는 속도감으로서의 밀도만 본다.

#### `pacing.paragraph` 단락 호흡 — Paragraph pacing
- 정의: 단락 길이와 그 변주. 한 줄 단락, 긴 논증 단락이 만드는 쉼과 몰입.
- 스펙트럼: 짧은 단락(웹·모바일형) ↔ 긴 단락(논설·학술형), 그리고 균일 ↔ 변주.
- 심사 질문: ① 단락 길이가 매체와 장르에 맞는가? ② 한 줄 단락이 강조 효과를 내는가, 남발되어 파편화되었는가? ③ 긴 단락이 한 가지 생각으로 묶여 있는가(길이 탓에 두 생각이 섞이지 않았는가)?
- 지시문 예: "한 줄 단락은 전환점에서만, 글 전체에 두 번까지." / "단락은 3~6문장 호흡을 기본으로 한다."
- 근거: 6+1 Trait Organization·Sentence Fluency; Clark *Writing Tools* 'Nuts and Bolts' 중 페이스 조절 도구들 [부분검증].
- 경계: 단락 **순서·구성**은 structure. 단락 요지문(point sentence)의 위치는 comprehension.

#### `pacing.zoom` 상술↔개괄 비율 — Detail zoom (scene ↔ summary)
- 정의: 어떤 대목은 느리게 확대해 보여 주고(장면, 세부), 어떤 대목은 빠르게 요약하는가. 전개 속도의 완급.
- 스펙트럼: 장면·세부(느림) ↔ 요약·개괄(빠름).
- 심사 질문: ① 중요한 대목에 충분한 해상도(세부)를 주었는가? ② 덜 중요한 대목에서 세부가 과해 늘어지지 않는가? ③ 확대와 축소가 번갈아 나와 리듬이 있는가?
- 지시문 예: "핵심 사례 하나는 장면으로 느리게 보여 주고 나머지는 한 문장 요약으로 넘긴다." / "배경 설명은 두 문장 안에서 개괄한다."
- 근거: Clark *Writing Tools* "Know the difference between reports and stories", "Mix narrative modes"(목록 항목명, [부분검증]); Biber Dimension 2(Narrative ↔ Non-narrative); [미검증] Genette의 서사 속도(장면/요약).
- 경계: 사례를 **넣을지**는 `illus`. 여기서는 넣은 사례를 어떤 속도로 전개하는지를 본다.

#### `pacing.momentum` 전진감·여담 허용도 — Momentum & digression
- 정의: 글이 목표를 향해 곧장 나아가는가, 샛길과 여담을 허용하는가. 긴장의 축적과 해소.
- 스펙트럼: 직진 ↔ 우회·산책.
- 심사 질문: ① 여담이 본론으로 되돌아오며 보상을 주는가? ② 독자가 "그래서 요점이 뭔데?"라고 느낄 지연이 있는가? ③ 긴 설명 구간 중간에 독자를 붙잡는 작은 보상(흥미로운 사실, 전환)이 배치되었는가?
- 지시문 예: "여담은 괄호 한 문장으로 끝내고 본론으로 돌아온다." / "에세이이므로 한 번의 긴 여담을 허용하되 결말에서 회수한다."
- 근거: Clark *Writing Tools* "Place gold coins along the path"(목록 항목명, [부분검증]); Hyland personal asides(기능은 engage에서 다룸).
- 경계: 여담의 **목소리(저자 논평)** 자체는 `engage.aside`. 여기서는 전개 속도에 미치는 영향만 본다.

### 2.5 `figure` — 수사 문채 (축: device)

고전 수사학의 scheme(배열의 일탈)과 trope(의미의 일탈) 구분(Silva Rhetoricae)에 한국 국어교육의 수사법 3분류(비유법·강조법·변화법)를 맞춰 넣었다.

#### `figure.imagery` 비유 — Figurative comparison
- 정의: 은유·직유·의인·환유 같은 닮음·인접 관계에 기댄 표현.
- 스펙트럼: 비유 없음(축자) ↔ 절제된 비유 ↔ 비유 중심.
- 심사 질문: ① 비유가 개념 이해나 정서 전달에 실제로 기여하는가(장식에 그치지 않는가)? ② 한 대목에서 서로 다른 비유가 섞여 충돌하지 않는가(mixed metaphor)? ③ 닳은 비유('빙산의 일각', '양날의 검')가 아닌가? (신선도는 `diction.freshness`와 교차 확인)
- 지시문 예: "비유는 섹션당 하나, 반드시 기술적 설명 뒤에 둔다." / "은유를 쓰면 같은 은유를 단락 끝까지 일관되게 유지한다."
- 근거: 비유법(직유·은유·의인·활유·환유·제유·풍유 등); Silva Rhetoricae trope; Leech & Short tropes(metaphor, metonymy, synecdoche).
- 경계: 설명 목적의 체계적 유추는 `illus.analogy`.

#### `figure.scheme` 배열 문채 — Schemes of arrangement
- 정의: 대구·대조(antithesis)·반복(anaphora 등)·점층(climax)·도치·교차대구(chiasmus)처럼 구조 배열로 효과를 내는 기법.
- 스펙트럼: 없음 ↔ 결정적 대목에만 ↔ 빈번.
- 심사 질문: ① 대구·대조가 실제로 대립되는 생각을 선명하게 하는가? ② 셋잇기(삼항 나열)가 습관처럼 반복되지 않는가(LLM 문체의 전형적 징후)? ③ 점층의 순서가 약한 것에서 강한 것으로 맞게 올라가는가?
- 지시문 예: "대조 구문은 핵심 논지에서 한 번만 쓴다." / "나열은 셋으로 맞추지 말고 실제 항목 수대로 쓴다."
- 근거: Silva Rhetoricae scheme(parallelism, antithesis, isocolon, climax); 강조법(반복·점층·대조·열거)·변화법(대구·도치); Leech & Short grammatical and lexical schemes; Clark "Choose the number of elements with a purpose in mind" [부분검증].
- 경계: 우연한 구조 반복으로 생긴 단조로움은 `cadence.variation`.

#### `figure.indirection` 간접 표현 — Tropes of indirection
- 정의: 말한 것과 뜻한 것이 어긋나게 만드는 기법. 반어(irony)·역설(paradox)·완서(litotes/understatement)·과장(hyperbole).
- 스펙트럼: 직설 ↔ 간접.
- 심사 질문: ① 반어나 과장이 오해 없이 읽히는가(문자 그대로 받아들여질 위험)? ② 과장이 사실 주장으로 오인될 수 있는 맥락(수치, 기술 문서)에 쓰이지 않았는가? ③ 완서('나쁘지 않다')가 필요 없는 모호함을 만들지 않는가?
- 지시문 예: "기술 문서에서는 과장과 반어를 쓰지 않는다." / "칼럼에서는 절제된 반어 한 번을 허용한다."
- 근거: Silva Rhetoricae(irony 등 trope); Leech & Short tropes(paradox, irony); 변화법(반어·역설), 강조법(과장).
- 경계: 과장이 **사실 왜곡**이 되면 evidence 문제로 넘긴다.

### 2.6 `engage` — 독자 관여 장치 (축: device)

Hyland(2005)의 engagement markers 5종(reader pronouns, directives, questions, appeals to shared knowledge, personal asides)을 그대로 말단으로 쓴다.

#### `engage.address` 독자 호명·포함 — Reader address
- 정의: '여러분', '당신', 독자를 포함하는 '우리'로 독자를 글 안에 불러들이는 정도.
- 스펙트럼: 호명 없음(3인칭 서술) ↔ 간헐 ↔ 대화형.
- 심사 질문: ① 호명 빈도와 방식이 지시에 맞는가? ② 포함적 '우리'가 독자에게 없는 전제를 떠넘기지 않는가? ③ '당신'이 거슬리거나 공격적으로 읽히지 않는가(한국어에서 '당신'은 민감)?
- 지시문 예: "독자는 '여러분'으로만 부르고 '당신'은 쓰지 않는다." / "설명은 3인칭으로 쓰고 실습 절에서만 독자를 부른다."
- 근거: Hyland engagement – reader pronouns; Federal Plain Language Guidelines의 독자 직접 호칭 권고 [부분검증]; Biber D1(2인칭 대명사 = involved).
- 경계: 호명이 만드는 관계의 느낌(위계)은 `tenor.distance`.

#### `engage.question` 질문 — Questions
- 정의: 수사의문, 설의(답이 정해진 의문), 독자에게 생각을 요구하는 실질 질문.
- 스펙트럼: 없음 ↔ 전략적 배치 ↔ 빈번.
- 심사 질문: ① 질문이 다음 내용을 여는 기능을 하는가, 답이 빤한 빈 질문인가? ② 연속 질문(질문 폭격)이 없는가? ③ 던진 질문에 글이 결국 답하는가?
- 지시문 예: "수사의문은 도입부에 하나만 쓰고 반드시 본문에서 답한다." / "'~하지 않을까요?'로 주장을 흐리지 않는다."
- 근거: Hyland engagement – questions; 변화법(설의·문답); Silva Rhetoricae rhetorical question.
- 경계: 도입의 **첫 문장**으로 쓰인 질문은 `frame.opening`에서도 함께 본다(기능은 여기, 위치 효과는 frame).

#### `engage.directive` 지시·권유 — Directives
- 정의: 명령('확인하라'), 청유('살펴보자'), 당위('~해야 한다')로 독자의 행동이나 사고를 이끄는 표현.
- 스펙트럼: 없음 ↔ 청유 중심 ↔ 명령 중심.
- 심사 질문: ① 지시 형식(명령·청유·당위)이 지정된 방식과 맞는가? ② 사고를 이끄는 지시('다음을 떠올려 보자')와 행동 지시('설정을 바꾼다')가 맥락에 맞게 쓰였는가? ③ '~해야 한다'가 과해 설교가 되지 않았는가?
- 지시문 예: "절차 안내는 명령형 대신 '~합니다' 서술형으로 쓴다." / "생각을 유도할 때는 '~해 보자' 청유형을 쓴다."
- 근거: Hyland engagement – directives; Biber Dimension 4(overt persuasion: 필요·예측 조동사, 설득 동사).
- 경계: 절차서의 **단계 구성**은 structure.

#### `engage.shared-ground` 공유 기반 호소 — Appeals to shared knowledge
- 정의: '누구나 한 번쯤', '알다시피', '흔히' 같은 말로 독자와의 공통 경험·지식을 불러 공감대를 세우는 기법.
- 스펙트럼: 없음 ↔ 절제 ↔ 빈번.
- 심사 질문: ① 공유를 가정한 지식이 대상 독자에게 실제로 공유되는가? ② '알다시피'가 모르는 독자를 소외시키지 않는가? ③ 공감 호소가 논증을 대신하지 않는가?
- 지시문 예: "'다들 알다시피', '당연히'는 쓰지 않는다." / "도입에서 독자가 겪었을 법한 상황 하나로 공감대를 만든다."
- 근거: Hyland engagement – appeals to shared knowledge.
- 경계: 전제 지식 수준을 맞추는 것 자체는 comprehension.

#### `engage.aside` 여담·괄호 논평 — Personal asides
- 정의: 괄호, 줄표, 삽입절로 흐름을 잠깐 끊고 저자가 독자에게 속삭이듯 건네는 논평.
- 스펙트럼: 없음 ↔ 드물게 ↔ 잦음(수다스러운 화자).
- 심사 질문: ① 여담이 친근함이나 뉘앙스를 더하는가, 흐름만 끊는가? ② 괄호 속에 본문에 있어야 할 핵심 정보가 숨지 않았는가? ③ 빈도가 지시에 맞는가?
- 지시문 예: "괄호 속 농담은 섹션당 하나까지." / "핵심 정보는 괄호에 넣지 않는다."
- 근거: Hyland engagement – personal asides; Leech & Short 'parenthetical structures'(문법 범주 General 항목) [미검증 세부].
- 경계: 여담이 **전개 속도**에 주는 영향은 `pacing.momentum`.

### 2.7 `illus` — 예시·사례 (축: device)

#### `illus.example` 예시 운용(추상의 사다리) — Exemplification
- 정의: 추상적 주장을 구체적 예로 내려 보여 주고 다시 원리로 올라오는 운용. 예시의 빈도, 전형성, 위치.
- 스펙트럼: 원리 선행(연역) ↔ 예시 선행(귀납), 그리고 예시 희소 ↔ 풍부.
- 심사 질문: ① 추상 층위에만 오래 머무는 구간(예시 없는 주장 연쇄)이 있는가? ② 예시가 주장을 정확히 보여 주는가(빗나간 예)? ③ 예시만 늘어놓고 원리로 올라오지 않는 구간이 있는가?
- 지시문 예: "추상적 주장 두 개가 이어지면 반드시 구체적 예를 하나 넣는다." / "예시는 원리 설명 직후에 두고 '예를 들어'로 시작하지 않는다."
- 근거: Hayakawa 추상의 사다리(Bessie → cow → livestock → farm assets → assets → wealth); Clark "Climb up and down the ladder of abstraction"(Tool 22); Strunk & White "Use definite, specific, concrete language" [부분검증].
- 경계: 단어 수준의 구체성은 `diction.concreteness`. 예시가 사실인지는 evidence.

#### `illus.anecdote` 일화·사례 서사 — Anecdote & case narrative
- 정의: 인물·시간·장소가 있는 작은 이야기(일화, 사례 연구, 가상 시나리오)를 설명이나 논증의 도구로 쓰는 것.
- 스펙트럼: 없음 ↔ 보조적 ↔ 서사 중심(내러티브 논픽션).
- 심사 질문: ① 일화가 요점을 담고 있는가, 요점과 따로 노는가? ② 가상 사례를 실제 사례처럼 제시하지 않는가(허구 표시)? ③ 일화 길이가 논지 비중에 맞는가?
- 지시문 예: "가상 시나리오는 '가령'으로 시작해 가상임을 밝힌다." / "각 장은 실무자 한 명의 짧은 사례로 연다."
- 근거: Clark "Get the name of the dog"(구체적 세부), "Report and write for scenes" [부분검증]; hook 유형론의 anecdotal hook.
- 경계: 실제 사례의 **사실성**은 evidence. 일화를 도입에 쓰는 **위치 효과**는 `frame.opening`.

#### `illus.analogy` 설명적 유추 — Explanatory analogy
- 정의: 낯선 체계를 익숙한 체계에 대응시켜 구조를 전달하는 유추(예: 캐시를 책상 위 메모에 빗대기).
- 스펙트럼: 없음 ↔ 핵심 개념에만 ↔ 빈번.
- 심사 질문: ① 대응 관계가 핵심 구조에서 성립하는가(어디서 깨지는지 밝혔는가)? ② 유추의 출처 영역이 대상 독자에게 익숙한가? ③ 유추가 기술적 정확성을 대신하지 않는가(유추 뒤에 정확한 설명이 오는가)?
- 지시문 예: "유추를 쓸 때는 한계를 한 문장으로 밝힌다." / "유추는 일상 사물에서만 가져온다."
- 근거: 비유법(풍유·비교); Silva Rhetoricae(analogy 계열 trope) [부분검증]. 설명 기능이 강해 `figure.imagery`에서 분리했다.
- 경계: 정서·미적 비유는 `figure.imagery`. 유추 뒤의 정확한 정의는 comprehension.

### 2.8 `frame` — 도입·마무리 (축: device)

#### `frame.opening` 도입 방식 — Opening move / hook
- 정의: 첫 한두 문장(또는 첫 단락)이 독자를 붙잡는 방식.
- 스펙트럼: 직입(요점부터) ↔ 후킹. 후킹 유형: 일화, 질문, 장면 묘사, 놀라운 사실·수치, 인용, 역설적 단언.
- 심사 질문: ① 도입 방식이 지시된 유형에 맞는가? ② 후킹이 본론과 이어지는가(낚시성 도입이 아닌가)? ③ '오늘날 ~는 매우 중요하다', '~에 대해 알아보자' 같은 상투적 도입이 아닌가?
- 지시문 예: "첫 문장은 구체적 장면이나 사실로 시작하고 '~에 대해 알아보자'로 시작하지 않는다." / "기술 문서는 첫 문장에 이 문서가 해결하는 문제를 쓴다."
- 근거: 에세이 hook 유형론(anecdotal, statistical, question, quotation, description hook); 수치 hook은 사실에 기반해야 한다는 조건.
- 경계: 도입 **섹션의 존재와 구성**(배경, 목적, 범위)은 structure. 도입에 쓴 수치가 정확한지는 evidence.

#### `frame.closing` 마무리 방식 — Closing move
- 정의: 마지막 한두 문장(또는 결말 단락)이 글을 닫는 방식.
- 스펙트럼(유형): 요약형 / 수미상관(도입의 일화·질문으로 회귀) / 함의·전망형 / 행동 촉구형 / 여운형(열린 결말) / 핵심 한 문장형.
- 심사 질문: ① 마무리 유형이 지시와 장르에 맞는가? ② 본문을 기계적으로 되풀이하는 요약이 아닌가('결론적으로, 앞서 살펴본 바와 같이')? ③ 도입에서 던진 질문과 일화를 회수했는가? ④ 새로운 주장을 결말에 처음 꺼내지 않았는가?
- 지시문 예: "결말에서 본문을 다시 요약하지 말고 독자가 내일 할 수 있는 행동 하나로 끝낸다." / "도입의 일화로 돌아가 닫는다."
- 근거: 결론 전략(echo the introduction, call to action, larger implication, forward-looking prediction; UMGC Writing Center 등); Clark "Write toward an ending" [부분검증].
- 경계: 결론 **섹션**의 필수 여부와 순서는 structure.

### 2.9 `diction` — 어휘 선택 (축: lexicon)

#### `diction.origin` 어종 — Lexical origin (고유어 ↔ 한자어 ↔ 외래어)
- 정의: 고유어, 한자어, 외래어·외국어의 비중과 선택.
- 스펙트럼: 고유어 중심 ↔ 한자어 중심 ↔ 외래어 허용.
- 심사 질문: ① 쉬운 고유어가 있는데 어려운 한자어나 외래어를 쓰지 않았는가(지시가 쉬운 말을 요구할 때)? ② 외래어를 쓸 때 독자층에 통용되는 말인가? ③ 고유어로 바꾸다가 오히려 뜻이 흐려지지 않았는가?
- 지시문 예: "'활용하다'보다 '쓰다'처럼 쉬운 고유어를 먼저 고른다." / "업계 통용 영어 용어는 그대로 쓰되 한글 표기를 따른다."
- 근거: 박갑수 문체론의 어휘 차원(고유어-한자어, 구체어-추상어); 국립국어원 공공언어 진단의 '어려운 외래어·한자어' 기준; Leech & Short lexical – general(formal/colloquial, rare/specialised vocabulary) [세부 미검증].
- 경계: 외래어 **표기법 준수**는 grammar(표기).

#### `diction.concreteness` 구체성 — Concreteness
- 정의: 감각할 수 있는 구체어를 쓰는가, 개념·범주어를 쓰는가.
- 스펙트럼: 추상 ↔ 구체.
- 심사 질문: ① '다양한 문제', '여러 측면' 같은 범주어로 끝나고 무엇인지 말하지 않는 곳이 있는가? ② 구체어가 필요한 곳(사례, 절차)에서 추상어로 흐리지 않았는가? ③ 반대로 일반화가 필요한 곳에서 세부에 갇히지 않았는가?
- 지시문 예: "'다양한', '여러 가지' 뒤에는 항목을 실제로 나열한다." / "성과는 형용사가 아니라 관찰 가능한 결과로 쓴다."
- 근거: Hayakawa 추상의 사다리; Strunk & White "Use definite, specific, concrete language" [부분검증]; Leech & Short lexical – nouns(abstract/concrete).
- 경계: 예시 **삽입**은 `illus.example`.

#### `diction.precision` 정밀성 — Precision (le mot juste)
- 정의: 뜻이 넓은 만능어('것', '부분', '관련', '진행', '대응')로 뭉뚱그리지 않고 정확한 단어를 고르는 것.
- 스펙트럼: 뭉뚱그린 말 ↔ 딱 맞는 말.
- 심사 질문: ① '~ 부분', '~ 관련', '~ 쪽' 같은 흐린 말이 구체적 단어를 대신하지 않는가? ② 비슷한 말(개선/향상/증진, 문제/오류/결함) 중 가장 정확한 것을 골랐는가? ③ 정도 부사('상당히', '꽤')가 숫자나 비교로 바뀌어야 할 자리에 쓰이지 않았는가?
- 지시문 예: "'관련', '부분'은 무엇과 어떻게 관련되는지 밝힐 수 있으면 쓰지 않는다." / "'문제'는 오류, 결함, 위험 가운데 정확한 말로 바꾼다."
- 근거: Leech & Short lexical – general(general vs specific); Williams concision의 "replace a phrase with a word".
- 경계: 뜻이 틀린 단어(오용)는 grammar.

#### `diction.technicality` 전문성 수준 — Technicality / jargon level
- 정의: 전문 용어와 업계 은어를 얼마나 쓰는가.
- 스펙트럼: 일상어 ↔ 전문어.
- 심사 질문: ① 대상 독자가 모르는 전문어를 필요 이상으로 쓰지 않는가? ② 전문가 독자에게 지나치게 풀어 쓰지 않는가? ③ 같은 개념에 전문어와 일상어를 뒤섞지 않는가?
- 지시문 예: "입문 독자용이므로 전문어는 꼭 필요한 것만 쓴다." / "사내 약어는 쓰지 않는다."
- 근거: Federal Plain Language Guidelines("write for your audience", avoid jargon); 국립국어원 쉬운 공공언어(소통성).
- 경계: **전문어를 처음 쓸 때 정의하는 것**, 용어 일관성은 comprehension. 여기서는 전문어를 쓸지 말지의 선택 경향만 본다.

#### `diction.ornament` 수식 밀도 — Ornamentation (건조체 ↔ 화려체)
- 정의: 형용사, 부사, 강조어('매우', '정말', '엄청난'), 미사여구의 양.
- 스펙트럼: 건조체(乾燥體: 수식 없이 요점만, 실용문) ↔ 화려체(華麗體: 수식어·미사여구가 많음, 예술문).
- 심사 질문: ① 수식어가 정보를 더하는가, 느낌만 부풀리는가? ② 강조 부사가 반복돼 강조가 닳지 않았는가? ③ 건조체를 요구받았을 때 너무 메말라 무엇이 중요한지 구분되지 않는가?
- 지시문 예: "'매우', '정말', '굉장히'는 쓰지 않는다." / "형용사는 명사 하나에 하나까지."
- 근거: 이태준 『문장강화』 건조체↔화려체(수식·미사여구의 유무); Williams concision("delete adjectives and adverbs"); Clark "Watch those adverbs" [부분검증].
- 경계: 비유(은유, 직유)는 `figure.imagery`. 평가어가 드러내는 **태도**는 `stance.attitude`.

#### `diction.economy` 어휘 경제 — Concision / needless words
- 정의: 뜻을 더하지 않는 말(겹말, 의미 없는 말, 추론 가능한 말, 구 대신 단어 하나로 될 말)을 덜어 내는 것.
- 스펙트럼: 군더더기 ↔ 절약(과하면 전보체).
- 심사 질문: ① 겹말('미리 예약', '다시 재개'), 빈 구('~라는 점에서', '~하는 것이 가능하다')가 있는가? ② 독자가 추론할 수 있는 말을 굳이 적었는가? ③ 절약이 지나쳐 조사와 연결어가 빠진 전보체가 되지 않았는가?
- 지시문 예: "'~하는 것이 가능하다'는 '~할 수 있다'로 줄인다." / "'기본적으로', '사실상' 같은 빈 부사는 뺀다."
- 근거: Strunk & White Rule 17 "Omit needless words"; Williams concision 규칙(delete meaningless words, doubled words, what readers can infer; replace a phrase with a word; change negatives to affirmatives).
- 경계: '~에 있어서', '~을 가지다'처럼 **번역투에서 온 군더더기는 grammar**. 판정이 겹치면 grammar를 우선한다. 문장 길이(호흡)는 `cadence.length`.

#### `diction.freshness` 신선도 — Freshness vs cliché
- 정의: 상투어, 닳은 관용구, 기계적 상용구를 피하는 정도. LLM 글에 흔한 상용구('~라고 할 수 있다', '중요한 역할을 한다', '다양한 측면에서', '결론적으로')도 여기에 든다.
- 스펙트럼: 상투적 ↔ 참신(과하면 기교적).
- 심사 질문: ① 어디서나 쓸 수 있는 문장, 즉 주제를 바꿔 넣어도 성립하는 문장이 있는가? ② 상용 연결구와 결론구가 반복되는가? ③ 참신함을 좇다 뜻이 어색해지지 않았는가?
- 지시문 예: "'중요한 역할을 한다', '~라고 할 수 있다'는 쓰지 않는다." / "관용구는 새로 쓸 수 있으면 새로 쓴다."
- 근거: Clark "Seek original images" [부분검증]; [미검증] Orwell "Politics and the English Language"(닳은 비유 금지 규칙); Leech & Short lexical – idioms·collocations.
- 경계: 금지어 목록 대조는 스크립트로 셀 수 있다. **목록 밖의 상투성**을 판정하는 것이 이 요소의 몫이다.

#### `diction.action` 행위 중심성 — Characters as subjects, actions as verbs
- 정의: 행위자를 주어로, 행위를 동사로 표현하는 경향. 명사화('검토를 실시하다', '개선이 이루어지다')와 정태적 표현을 덜 쓰고 힘 있는 동사를 고른다.
- 스펙트럼: 명사화·정태적 ↔ 동사·행위자 중심.
- 심사 질문: ① 주요 행위가 명사 속에 묻혀 있지 않은가('~의 강화를 통한 ~의 제고')? ② 누가 하는지 밝혀야 할 곳에서 행위자가 사라지지 않았는가? ③ '하다·되다·이루어지다'처럼 힘없는 동사 대신 구체 동사를 고를 수 있는가?
- 지시문 예: "행위는 동사로 쓴다. '분석을 수행한다'가 아니라 '분석한다'." / "책임 주체가 있는 문장은 그 주체를 주어로 쓴다."
- 근거: Williams *Style* 핵심 원칙("Make central characters subjects… use verbs to name the actions"); Strunk & White "Use the active voice"; Biber Dimension 1 informational 극의 명사화.
- 경계: **번역투 피동('~되어지다'), '~에 의해', 이중 피동은 grammar**. 이 요소는 문법적으로 자연스러운 문장이 밋밋할 때 더 힘 있는 쪽을 고르는 문체 선호만 다룬다. 판정 규칙: 비문이나 부자연이면 grammar, 자연스럽지만 약하면 lexicon.

#### `diction.repetition` 반복 ↔ 바꿔 쓰기 — Repetition vs elegant variation
- 정의: 같은 대상을 같은 말로 반복하는가, 동의어로 바꿔 가며 쓰는가(elegant variation).
- 스펙트럼: 동어 유지 ↔ 변이.
- 심사 질문: ① 같은 대상을 여러 이름으로 불러 독자가 다른 대상으로 오해할 위험이 있는가(기술 문서)? ② 문학·에세이에서 같은 단어가 가까이 반복돼 거슬리는가? ③ 의도적 반복(강조)과 무심한 반복이 구별되는가?
- 지시문 예: "기술 개념은 처음 정한 이름을 끝까지 쓴다." / "에세이에서 같은 서술어를 한 단락에서 두 번 넘게 쓰지 않는다."
- 근거: Leech & Short cohesion 항목의 'elegant variation'(반복 대신 기술적 구로 대체); 우아한 변이의 함정에 대한 전통적 문체 지침 [부분검증].
- 경계: **용어 일관성을 지키는 목적이 이해도**일 때는 comprehension이 우선한다. 이 요소는 장르에 따른 반복과 변이의 미적 선택만 다룬다.

---

## 3. 이 분류에 넣지 말아야 할 것 (타 층 소유)

| 현상 | 소유 층 | 이유와 경계선 |
|---|---|---|
| 섹션 존재·순서, 문서 유형별 골격, 결론 섹션 유무, 반론 섹션 | **structure** | voice는 "어떻게 말하나"만 본다. `frame.*`는 첫·끝 문장의 **움직임**이지 섹션 설계가 아니다. |
| 문서 수준 두괄식·미괄식 배치 | **structure** | 문장 내 강조 위치(`cadence.emphasis`)와 구별한다. |
| 사실·수치·인용의 정확성, 출처 적절성, 과장이 사실 왜곡이 되는 경우 | **evidence** | `stance.certainty`는 **글이 제시한 근거 대비** 언어적 확신만 본다. |
| 번역투('~에 있어서', '~을 가지다', '~적' 남발, 이중 피동, '~에 의해'), 맞춤법, 띄어쓰기, 조사 오용, 호응 오류, 비문, 외래어 표기 | **grammar** | 이오덕 『우리글 바로 쓰기』 계열. `diction.action`·`diction.economy`와 겹치면 grammar 우선(비문·부자연 = grammar, 자연스럽지만 약함 = lexicon). |
| 용어 첫 정의, 점진적 공개, 전제 지식 수준, 용어 일관성(이해 목적), 지시어 명확성 | **comprehension** | `diction.technicality`는 전문어 사용 **경향**만, `diction.repetition`은 미적 선택만. |
| 구정보→신정보 흐름, topic string(주제 연쇄), 단락 요지문 위치, 접속 관계 명시 | **comprehension** | Williams의 cohesion·coherence 원칙은 이해 가능성 도구다. voice의 `cadence.emphasis`는 **수사적 힘**만 다룬다. |
| 평균·최대 문장 길이, 종결어미 비율, 금지어 등장 수, 한 줄 단락 수, 연속 동일 어미 수 | **정량 게이트(스크립트)** | 정성 요소는 해당 수치의 **적합성**만 판정한다. 지시문이 수치를 담으면("40자 이내") 정량 게이트로 보내는 것이 맞다. |
| 내용의 참신성, 논지의 타당성, 아이디어의 질 | (voice 밖, 내용/evidence) | 6+1 Trait의 Ideas는 문체가 아니다. |

**분류기 규칙 제안**: 지시문 입력 시 ① 수치나 목록 대조만으로 판정 가능하면 정량으로 보낸다. ② 위 표의 현상이면 해당 층으로 보낸다(예: "용어는 처음 나올 때 정의한다" → comprehension). ③ 나머지를 이 트리의 말단에 붙인다. 한 지시문이 두 말단에 걸치면 **판정 질문이 더 직접 적용되는 쪽** 하나에만 붙이고 분리를 권한다.

---

## 4. LLM 심사관 운용 메모

- **판정 단위**: 지시문 하나마다 "준수 / 부분 위반 / 위반"과 근거 구절 인용(최대 3곳)을 낸다. 스펙트럼형 요소는 "지시 위치 대비 실제 위치"를 짧게 서술한다(예: "지시: 우유체 / 실제: 결말 2단락이 강건체로 기움").
- **장르 적합성 기본 질문**(모든 register 요소에 공통): Halliday field·tenor·mode, 즉 무엇을, 누구에게, 어떤 채널로 쓰는 글인지를 먼저 확인한 뒤 판정한다.
- **일관성은 말단이 아니라 메타 규칙이다**: 모든 스펙트럼 요소에 "글 전체에서 흔들리지 않는가? 흔들림은 의도적인가?"를 공통으로 묻는다(Leech & Short Context 항목의 '화자에 따른 문체 변화').
- **LLM 문체 징후와 대응 요소**: 셋잇기 나열(`figure.scheme`), 상투 결론구(`diction.freshness`, `frame.closing`), 과잉 유보(`stance.certainty`), '다양한/여러' 범주어(`diction.concreteness`), 빈 수사의문(`engage.question`), 균일한 문장 길이(`cadence.variation`).

---

## 5. 설계상 선택지와 미결 사항

1. **말단 40~41개가 많다고 느껴지면**: `illus.analogy`를 `figure.imagery`에 합치고, `pacing.momentum`을 `pacing.zoom`에 합치면 39개가 된다. 더 줄이려면 `engage.aside`를 `engage.address`에 합쳐 38개.
2. **`tenor.speech-level`을 register에 둘지 grammar에 둘지**: 종결 등급의 **일관성**은 기계적이므로 스크립트나 grammar로 보내고, **선택과 전환의 적합성**만 register에 둔다(현재 안).
3. **`diction.ornament`(건조↔화려)를 device로 옮길지**: 이태준 정의가 '수식·미사여구'이고 박갑수는 이를 '수사' 차원에 넣었다. 하지만 비유를 뺀 수식어 밀도는 단어 선택이므로 lexicon에 두었다. 비유 밀도까지 합친 '화려도' 지시문이 들어오면 `diction.ornament`로 받고 `figure.imagery`를 보조로 참조한다.
4. **`stance.force`와 `tenor.key`**: "강하게"는 force, "가볍게"는 key. 사용자 지시문이 "톤"이라는 말 하나로 둘을 섞는 경우가 많으므로, 분류 UI에서 "세기(강↔약)인가, 무게(진지↔경쾌)인가"를 되묻는 것이 좋다.
5. **한국어 다차원 분석(Kim & Biber 1994)**: 차원 구성의 세부(honorification 외)는 확인하지 못했다 [부분검증]. 한국어 사용역 차원을 더 반영하려면 원문 확인이 필요하다.

---

## 6. 출처 목록

(검증 = WebSearch 스니펫으로 내용 확인. [부분검증] = 일부 항목만 확인. [미검증] = 기억·2차 지식)

### 문체론 체크리스트
- Leech & Short 체크리스트 요약(uv.es): https://www.uv.es/~tronch/stu/CommentTextsGuideChecklist.html — 4대 범주(Lexical / Grammatical / Figures of speech / Cohesion & Context). 페이지 직접 열람은 차단, 검색 스니펫으로 확인. [부분검증]
- Makhloof, "Leech and Short's Checklist of Lexical Features": https://ijohmn.com/index.php/ijohmn/article/view/189 — 어휘 범주의 하위 구분 general / nouns / adjectives / verbs / adverbs. 검증.
- ERIC EJ1128146(Leech & Short 적용 분석): https://files.eric.ed.gov/fulltext/EJ1128146.pdf — 4개 층위, "systematic basis", elegant variation, 대명사·대용형·생략에 의한 cross-reference, anticipatory structure, addresser. 스니펫 검증.
- ResearchGate 체크리스트 표(Leech & Short 2007): https://www.researchgate.net/figure/A-Checklist-of-linguistic-and-stylistic-categories-Leech-and-Short-2007_tbl1_366469614 — 표 존재 확인. 세부 [미검증].
- *체크리스트 세부 하위 항목(문장 유형, 복잡도, 절 유형, 명사구·동사구, 음운 도식, tropes, 연결·문맥)은 기억에 의존한 부분이 있다. [부분검증]*

### 사용역·격식
- Glottopedia "Register (discourse)": http://glottopedia.org/index.php/Register_(discourse) — Halliday field / tenor / mode 정의. 검증(스니펫).
- The Thought Occurs(Halliday & Hasan 해설): https://thethoughtoccurs.blogspot.com/2016/04/halliday-hasan-on-field-mode-and-tenor.html — field↔experiential, tenor↔interpersonal, mode↔textual. 검증(스니펫).
- Joos, *The Five Clocks* (Google Books): https://books.google.com/books/about/The_Five_Clocks.html?id=usZrzy0gkOEC — frozen / formal / consultative / casual / intimate. 검증(스니펫).
- Biber MD 차원(Nature HSSC 2024): https://www.nature.com/articles/s41599-024-02968-9 — 5개 차원(Involved↔Informational, Narrative, Situation-dependent↔Explicit, Overt persuasion, Abstract). 검증.
- Bamberg "Dimensions of English": https://www.uni-bamberg.de/fileadmin/eng-ling/fs/Chapter_21/23DimensionsofEnglish.html — Dimension 1 특징(private verbs, contractions, 2인칭, hedges, amplifiers ↔ nouns, prepositions, attributive adj). 검증(스니펫).
- Biber, "Using multi-dimensional analysis to explore cross-linguistic universals": https://benjamins.com/catalog/lic.14.1.02bib — Kim & Biber(1994) 한국어 MD, honorification 차원 언급. [부분검증]

### 입장·관여
- Hyland 2005 상호작용 모형(ERIC EJ1314916): https://files.eric.ed.gov/fulltext/EJ1314916.pdf — hedges, boosters, attitude markers, self-mention, engagement markers(reader pronouns, personal asides, shared knowledge, directives, questions). 검증(스니펫).
- Martin & White 3장 샘플: https://www.prrwhite.info/Martin%20and%20White,%202005,%20CHPT%203%20(sample)%20The%20Language%20of%20Evaluation.pdf — Appraisal = Attitude / Engagement / Graduation. Attitude = affect / judgement / appreciation. 검증(스니펫).
- Munday, Engagement & Graduation(White Rose): https://eprints.whiterose.ac.uk/id/eprint/92141/1/Munday_Target_accepted.pdf — Graduation = Force(세기) / Focus(선명도), monogloss / heterogloss. 검증(스니펫).
- PolyU Engagement 해설: http://www.engl.polyu.edu.hk/academic_writing/engagement.html — contract(disclaim: deny/counter, proclaim: concur/pronounce/endorse) ↔ expand(entertain, attribute: acknowledge/distance). 검증(스니펫).

### 명료성·우아함
- Williams & Bizup *Style* PDF: https://www.clc.hcmus.edu.vn/wp-content/uploads/2015/11/Style_-_Joseph_M._Williams_Joseph_Bizup.pdf — 원전(직접 열람 불가).
- Archbee 서평: https://www.archbee.com/blog/book-review-joseph-m-williams-style-lessons-in-clarity-and-grace — "characters as subjects, actions as verbs". 검증.
- Antoine Buteau 요약 / SDSU 노트: https://www.antoinebuteau.com/lessons-from-joseph-m-williams-joseph-bizup/ , https://sdsuwriting.pbworks.com/f/Style_BIG_COLLECTION_COMPILED.doc — topic strings, old→new, stress position, cohesion vs coherence. 검증(스니펫).
- NYSBA, Williams Part II: https://nysba.org/thoughts-on-legal-writing-from-the-greatest-of-them-all-joseph-m-williams-part-ii/ — concision 규칙(meaningless / doubled / inferable words 삭제 등), shape와 sprawl, resumptive / summative / free modifier. 검증(스니펫).
- Cornell Chronicle, Strunk & White 50주년: https://news.cornell.edu/stories/2009/03/omit-needless-words-elements-style-turns-50 — Omit needless words, active voice, positive form. 검증. "Use definite, specific, concrete language", "Place the emphatic words at the end"는 원문 확인 못 함. [부분검증]
- Digital.gov 쉬운 글쓰기 원칙: https://digital.gov/guides/plain-language/principles — write for your audience, short sentences, active voice. 검증.
- Federal Plain Language Guidelines(2011): https://wid.org/wp-content/uploads/2022/03/FederalPLGuidelines.pdf — 원전(직접 열람 불가).
- Hayakawa 추상의 사다리(Big Think): https://bigthink.com/the-learning-curve/ladder-of-abstraction/ — Bessie → cow → livestock → farm assets → assets → wealth. 검증.
- Poynter, Fifty Writing Tools Quick List: https://www.poynter.org/reporting-editing/2006/fifty-writing-tools-quick-list/ — "Order words for emphasis", "Fear not the long sentence", Tool 22 "Climb up and down the ladder of abstraction", "Set the pace with sentence length". 앞의 둘은 스니펫으로 검증, 그 밖의 도구명(gold coins, name of the dog, write toward an ending, watch those adverbs 등)은 [부분검증].
- Education Northwest 6+1 Trait: https://educationnorthwest.org/resources/61-trait-rubrics — Voice, Word Choice, Sentence Fluency("plays to the ear") 정의. 검증.

### 리듬·문장 형상
- Aerogramme, Provost "This sentence has five words": https://www.aerogrammestudio.com/2014/08/05/this-sentence-has-five-words/ — 문장 길이 변주 = 음악. 검증.
- KUMC Writing Center, periodic vs loose: https://www.kumc.edu/Documents/counseling/Periodic%20and%20Loose%20Sentences.pdf — 도미문(긴장·강조) vs 산열문(즉시성). 검증(스니펫).
- Atlantis Press, end-weight 원리: https://www.atlantis-press.com/article/25847866.pdf — Quirk end-focus / end-weight 정의와 구분. 검증(스니펫).

### 수사 문채
- Silva Rhetoricae(BYU) scheme / trope: https://rhetoric.byu.edu/Figures/Scheme.htm , https://rhetoric.byu.edu/Figures/Trope.htm — 배열 일탈(scheme)과 의미 일탈(trope), parallelism / antithesis / isocolon / climax / rhetorical question / irony. 검증(스니펫).
- 수사법 3분류(브런치): https://brunch.co.kr/@heir480/1448 — 비유법 / 강조법 / 변화법 하위 목록. 검증(스니펫). 교과서 원문은 [미검증].

### 도입·마무리
- Grammarly, hook 작성: https://www.grammarly.com/blog/writing-tips/how-to-write-a-hook/ ; Writers@Work hook 유형: https://www.writersatwork.com.sg/good-hooks-for-essay-introductions/ — anecdotal / statistical / question / quotation / description hook. 검증.
- UMGC 결론 작성: https://www.umgc.edu/current-students/learning-resources/writing-center/writing-resources/writing/essay-conclusions — echo the introduction, call to action, implication. 검증(스니펫).

### 한국어 문체론·작문
- 위키문헌 『문장강화』: https://ko.wikisource.org/wiki/%EB%AC%B8%EC%9E%A5%EA%B0%95%ED%99%94 ; 창비 개정판: https://www.changbi.com/BookDetail?bookid=1296 — 제7강 '대상과 표현', 제8강 '문체에 대하여'(문체의 발생, 문체의 종별). 검증(스니펫).
- 문체 분류 요약(다음 블로그·위키백과 '문체'): https://ko.wikipedia.org/wiki/%EB%AC%B8%EC%B2%B4 — 간결↔만연(구절의 길이), 강건↔우유(표현의 세기), 건조↔화려(수식 유무). 스니펫으로 검증. 『문장강화』 원문 대조는 [미검증].
- 한국민족문화대백과 '문체': https://encykorea.aks.ac.kr/Article/E0019695 — (열람 차단) [미검증]
- 박갑수 문체론 요약(다음 블로그 '문체와 사회'): https://m.blog.daum.net/60-gkdis/2503106 — 문체 요소 = 표기, 어휘(고유어-한자어, 구체어-추상어), 어법(경어체·반말체), 수사(건조-화려 포함), 문장 형식(홑·겹문, 간결·만연). 2차 블로그 출처 [부분검증].
- 국립국어원 온라인가나다 '구어체 문어체 구분': https://www.korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=&qna_seq=326949&pageIndex=1 — 해요체→하십시오체, '거'→'것'. 검증(스니펫).
- 한국어 상대높임법(KCI 박지순 논문): http://emunhak.com/chart/73_05_parkjs.pdf — 격식체 4등급 / 비격식체 2등급. 검증(스니펫).
- 법제처, 공공언어 소통성·정확성: https://moleg.go.kr/mpbleg/mpblegInfo.mo?mid=a10402020000&mpb_leg_pst_seq=132081 — 쉬운 공공언어 요건(소통성: 용이성·정보성·공공성 / 정확성), 진단 기준(문장 길이, 권위적·차별적 표현, 어려운 외래어·한자어). 검증(스니펫).
- 국립국어원 '행정문서 표현 개선 및 쉬운 공공언어 쓰기 지침': https://www.korean.go.kr/front/reportData/reportDataView.do?mn_id=45&searchOrder=&report_seq=1122&pageIndex=1 — 원전(열람 불가).
- KCI '국어 텍스트의 장르별 초기 문체 특징과 비교: 문장 종결 양상을 중심으로': https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART000878822 — 종결 양상이 장르 문체의 지표. 제목만 확인 [부분검증].
- 이오덕 『우리글 바로쓰기』(위키백과): https://ko.wikipedia.org/wiki/%EC%9A%B0%EB%A6%AC%EA%B8%80_%EB%B0%94%EB%A1%9C%EC%93%B0%EA%B8%B0 — '~적', 번역 피동 비판. grammar 층 경계의 근거. 검증(스니펫).

### 미검증 인용(사용 시 원문 확인 필요)
- Hymes SPEAKING 모델의 'Key'(`tenor.key`)
- Genette 서사 속도(장면/요약)(`pacing.zoom`)
- Orwell "Politics and the English Language" 규칙(`diction.freshness`)
- Leech & Short 문법 범주 세부(parenthetical structures 등)
