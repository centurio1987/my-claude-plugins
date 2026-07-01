# Graphify 통합 레퍼런스

`wiki-forge`의 Phase 0(프리플라이트)·Phase 3(그래프 레이어 배선)에서 사용한다.

> ⚠️ **버전 대조 필수:** 아래 명령 표면은 graphify 공개 문서(`github.com/safishamsi/graphify`) 기반이다.
> 배포 버전에 따라 옵션이 다를 수 있으므로, **쓰기 전에 반드시 `graphify --version` + `graphify --help`(하위 명령 포함)로 실제 지원 여부를 대조**하고, 다르면 지원되는 명령으로 폴백한다.

---

## 1. 설치 & 등록

```bash
uv tool install graphifyy     # PyPI 패키지명은 graphifyy (y 두 개) — CLI 명령은 graphify
graphify install              # graphify를 Claude Code 스킬로 등록 (/graphify 사용 가능)
graphify claude install       # 위키 루트에 상시 지침 + PreToolUse 훅 등록
```

- 전제: Python 3.10+, `uv` 패키지 매니저.
- `graphify claude install`은 파일/훅을 변경하므로 **실행 전 `graphify claude install --help`로 변경 범위(기존 CLAUDE.md·사용자 훅 덮어쓰기 여부)를 확인**하고 사용자에게 알린다. 이미 등록돼 있으면 재등록하지 않는다.

## 2. 빌드 / 갱신

```bash
graphify .                    # 현재 디렉토리 전체 → graphify-out/ 생성
graphify . --update           # 변경된 파일만 재추출
graphify . --cluster-only     # 재추출 없이 클러스터링만 다시
```

**초기 빌드 타이밍:** 스캐폴딩 직후 `raw/`·`wiki/`가 비어 있으면 빌드가 실패하거나 무의미한 그래프만 나온다.
→ **최초 소스를 ingest한 뒤** 첫 `graphify .`를 실행한다. 이후 ingest마다 `graphify . --update`.

## 3. 산출물 (`graphify-out/`)

| 파일 | 내용 |
|------|------|
| `graph.html` | 인터랙티브 시각화 (노드 클릭·필터·검색) — 브라우저로 연다 |
| `GRAPH_REPORT.md` | 하이라이트(허브 노드·의외의 연결·근거 추출) |
| `graph.json` | 재조회용 전체 그래프 (파싱 가능해야 함 = 완료 판정 지표 중 하나) |

## 4. 조회 명령

```bash
graphify query "auth와 database를 잇는 게 뭐지?"   # 의미/관계 질의
graphify path "UserService" "DatabasePool"         # 두 엔티티 간 경로
graphify explain "RateLimiter"                      # 특정 노드 설명
```

**조회 정책(완화):** 의미·관계 질의는 graphify, **정확 문자열·파일 위치 검색은 grep/rg**. graphify를 전면 강제하지 않는다.

## 5. 인덱싱 경계 (include / exclude)

- **반드시 제외:** `graphify-out/` — 자기 생성물이라 재인덱싱하면 잡음·재귀 입력이 된다.
- **검토 후 제외:** 비밀/개인 파일 경로(토큰·자격증명·비공개 노트).
- `raw/` 포함 여부는 도메인에 맞게 CLAUDE.md에 명시한다(원본까지 그래프에 넣을지 결정).
- git 저장소면 `graphify-out/`을 `.gitignore`에 중복 없이 추가한다.

## 6. 프라이버시 노트

graphify는 LLM 기반 추출로 콘텐츠를 처리한다. 민감 자료를 넣기 전에:
- 콘텐츠가 외부 API로 전송되는지 / 로컬에서 처리되는지 사용자에게 고지한다(배포 구성에 따라 다를 수 있으므로 확정적으로 단언하지 말고 확인하도록 안내).
- 비밀·개인 파일은 `raw/` 밖에 두거나 위 exclude 경계로 관리하도록 권고한다.

## 7. CLAUDE.md 삽입 스니펫 (멱등 마커 포함)

아래 블록을 위키 루트의 `CLAUDE.md`에 삽입한다. **시작/끝 마커로 감싸** 재실행 시 마커 사이만 갱신하고 중복 삽입하지 않는다(마커가 이미 있으면 그 구간을 교체, 없으면 신규 추가).

```markdown
<!-- wiki-forge:graphify:start -->
## Graphify 지식그래프 레이어

이 위키는 graphify로 쿼리 가능한 지식 그래프를 유지한다.

### 조회
- 의미·관계 질의: `graphify query "<질문>"`, `graphify path "<A>" "<B>"`, `graphify explain "<노드>"`
- 정확한 문자열·파일 위치 검색: `grep`/`rg` 사용 (graphify를 강제하지 않는다)

### 그래프 유지
- 최초: 첫 소스를 `raw/`에 넣고 ingest한 뒤 `graphify .` 로 최초 그래프 생성
- 이후 ingest마다: `graphify . --update` 로 변경분만 재추출
- 시각화 확인: `graphify-out/graph.html` 을 브라우저로 연다

### 인덱싱 경계
- `graphify-out/` 은 그래프 대상에서 제외 (생성물·재귀 방지)
- 비밀/개인 파일은 그래프 대상에서 제외
<!-- wiki-forge:graphify:end -->
```

## 8. 트러블슈팅

| 증상 | 대응 |
|------|------|
| `command -v graphify` 실패(설치했는데) | `~/.local/bin/graphify`, `$(uv tool dir)` 하위 탐색 → `uv tool update-shell` → 새 셸 |
| `graphify .` 빌드 실패 | 입력이 비었는지 확인 → 최초 소스 ingest 후 재시도 |
| CLAUDE.md/훅 중복 | 마커(`wiki-forge:graphify:*`)·기존 훅 등록 감지 후 갱신(재삽입 금지) |
| 옵션 미지원 오류(`--update` 등) | `graphify --help`로 지원 명령 확인 후 대체(전체 재빌드 `graphify .` 등) |
| 재빌드 타이밍 | 콘텐츠가 크게 바뀐 뒤에만. 매 편집마다 돌릴 필요 없음 |
