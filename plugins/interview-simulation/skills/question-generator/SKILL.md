---
name: question-generator
description: >
  This skill should be used when the user asks to "질문 생성해줘", "면접 질문 만들어줘",
  "포지션별 질문 뽑아줘", "인터뷰 준비해줘", or wants to generate an interview question
  sheet for a specific position. Produces a Korean-language markdown question sheet
  with importance and difficulty labels for one interview session.
metadata:
  version: "0.1.0"
---

# 질문 생성 스킬

사용자가 특정 포지션의 면접을 준비할 수 있도록 1회 인터뷰 분량(10~15문항)의 질문지를 한국어 마크다운으로 생성한다.

## 실행 순서

### 1단계: 포지션 및 디테일 수집

다음 정보를 사용자에게 확인한다 (이미 알고 있는 항목은 건너뛴다):

- **포지션** (필수): 아래 프리셋 중 선택하거나 직접 입력
  - `node.js engineer`, `devops engineer`, `product engineer`, `cto`, `product owner`
- **경력 연차** (필수): 예) "4년", "주니어", "시니어"
- **포지션 디테일** (선택): 목표 회사 규모/도메인, 강조할 기술 스택, 특이사항

### 2단계: 이력서 로드

`/Users/centurio/resume` 디렉토리에서 다음 파일을 Read 도구로 읽는다:
- `README.md` — 경력 요약
- `CLAUDE.md` — 포트폴리오/역량 메모
- `skills/` 디렉토리 내 파일들

접근이 불가능하면 사용자에게 이력서 주요 내용을 직접 입력해달라고 요청한다.

### 3단계: 최신 면접 질문 트렌드 수집

WebSearch 도구로 아래 쿼리를 실행한다:
- `"[포지션] 면접 질문 [현재연도]"`
- `"[포지션] interview questions [현재연도]"`

검색 결과에서 최근 1~2년 내 빈출 주제와 새로운 트렌드를 파악한다.

### 4단계: 프리셋 참조

`references/position-presets.md`에서 해당 포지션의 핵심 개념 리스트를 읽어 다음을 확인한다:
- 반드시 커버해야 할 핵심 개념 영역
- 경력 연차에 맞는 강조 포인트

### 5단계: 질문지 생성

`references/question-format.md`의 포맷을 따라 질문지를 생성한다.

**구성 원칙**:
- 총 10~15문항
- 중요도 분포: ⭐⭐⭐ 4~5개, ⭐⭐ 4~6개, ⭐ 2~3개
- 난이도 분포: Hard 3~4개, Medium 5~7개, Easy 2~3개
- 이력서에서 발견한 경험/프로젝트를 기반으로 맞춤형 질문 1~3개 포함
- 인터넷 트렌드에서 수집한 최신 질문 2~3개 포함
- 모든 질문은 한국어로 작성

**포함 필드** (질문당):
- 질문 내용
- 중요도 레이블 (⭐/⭐⭐/⭐⭐⭐)
- 난이도 레이블 (Easy/Medium/Hard)
- 의도 (한 줄 설명)
- 키워드 (예상 답변의 핵심 키워드 3~5개)

### 6단계: 출력

질문지를 대화 창에 직접 출력한다. 파일 저장이 필요하면 사용자에게 확인 후 Write 도구로 저장한다.
파일명 규칙: `interview-[포지션]-[YYYYMMDD].md`
