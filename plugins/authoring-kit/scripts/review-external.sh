#!/usr/bin/env bash
# 외부 검토 — 글을 codex CLI(ChatGPT)와 antigravity CLI(agy/Gemini)에 병렬로 보내 약점을 받는다.
#
# 세 프로젝트가 거의 같은 스크립트를 하나씩 들고 있었다(review-article.sh / review-guide.sh /
# review-problem.sh). diff 는 **프롬프트 3축 텍스트뿐**이었다. 그래서 축을 파일로 빼고 하나로 합쳤다.
#
#   review-external.sh <파일> --axes <축파일> [--redact <프로파일>] [--policy hard-fail|warn]
#
# --axes    검토 3축 프롬프트 파일(글 종류별). 없으면 범용 축을 쓴다.
# --redact  외부로 보내기 전 개인정보를 토큰으로 치환한다. 이력서처럼 실명·연락처가 든 글은
#           반드시 준다. 복원 매핑은 로컬 임시파일에만 두고 종료 시 지운다.
# --policy  두 도구 모두 실패했을 때. hard-fail(기본, exit 2) | warn(exit 0, 경고만)
#
# 필요: codex 와/또는 agy CLI 설치·인증. 둘 중 하나만 응답해도 진행하되 어느 쪽이 빠졌는지 보고한다.

set -u

CODEX_MODEL="${CODEX_MODEL:-}"
AGY_MODEL="${AGY_MODEL:-}"
CALL_TIMEOUT="${REVIEW_ARTICLE_TIMEOUT:-420}"

err() { printf '%s\n' "$*" >&2; }

TIMEOUT_CMD=""
if command -v timeout >/dev/null 2>&1; then
  TIMEOUT_CMD="timeout"
elif command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_CMD="gtimeout"
fi
run_limited() {
  if [ -n "$TIMEOUT_CMD" ]; then
    "$TIMEOUT_CMD" "$CALL_TIMEOUT" "$@"
  else
    "$@"
  fi
}

ARTICLE_FILE=""
AXES_FILE=""
REDACT="none"
POLICY="hard-fail"
while [ $# -gt 0 ]; do
  case "$1" in
    --axes)   AXES_FILE="${2:-}"; shift 2 ;;
    --redact) REDACT="${2:-none}"; shift 2 ;;
    --policy) POLICY="${2:-hard-fail}"; shift 2 ;;
    -h|--help) err "사용법: review-external.sh <파일> --axes <축파일> [--redact <프로파일>] [--policy hard-fail|warn]"; exit 0 ;;
    *) ARTICLE_FILE="$1"; shift ;;
  esac
done

if [ -z "$ARTICLE_FILE" ]; then
  err "사용법: review-external.sh <파일> --axes <축파일> [--redact <프로파일>] [--policy hard-fail|warn]"
  exit 1
fi
if [ ! -r "$ARTICLE_FILE" ]; then
  err "파일을 읽을 수 없습니다: $ARTICLE_FILE"
  exit 1
fi
if [ ! -s "$ARTICLE_FILE" ]; then
  err "파일이 비어 있습니다: $ARTICLE_FILE"
  exit 1
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN="$(dirname "$HERE")"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT      # 복원 매핑까지 함께 지운다

# ── redaction — 외부로 나가기 전에 개인정보를 토큰으로 바꾼다 ─────────────
# 이력서 본문에는 실명·연락처·회사명·재직기간이 들어 있다. 검토 품질을 위해 구조는 남기고
# 식별자만 가린다. 복원 매핑은 TMP_DIR 에만 두고 종료 시 지운다(trap).
BODY_FILE="$TMP_DIR/body.txt"
cp "$ARTICLE_FILE" "$BODY_FILE"
REDACT_NOTE=""
if [ "$REDACT" != "none" ]; then
  # 프로파일은 **한 파일이 아니라 계층이다.** 플러그인 저장소는 PUBLIC 이라
  # 실명·이메일 같은 고유 리터럴이 거기 있으면 안 된다 — 가리려던 것을 스스로 공개하는 꼴이다.
  #   ① 플러그인   구조적 패턴(이메일·전화·주민번호 정규식) — 누구에게나 같다
  #   ② 사용자     `$AUTHORING_KIT_HOME/redact/` — 실명·핸들 같은 고유 리터럴. PRIVATE 저장소
  #   ③ 프로젝트   `<project>/.claude/authoring/redact/` — 그 프로젝트만의 리터럴
  # 하나만 고르지 않고 **이어 붙인다.** 계층 순서가 곧 올바른 적용 순서다 —
  # 프로파일이 스스로 적어 둔 원칙("넓은 패턴을 먼저, 좁은 리터럴을 나중에")과 같다.
  PROFILE_FILE="$TMP_DIR/redact.merged"
  : > "$PROFILE_FILE"
  layers=0
  for d in "$PLUGIN/skills/authoring-method/assets/redact" \
           "${AUTHORING_KIT_HOME:-$HOME/.claude/authoring}/redact" \
           "$(dirname "$ARTICLE_FILE")/../.claude/authoring/redact"; do
    if [ -r "$d/$REDACT.txt" ]; then
      cat "$d/$REDACT.txt" >> "$PROFILE_FILE"
      printf '\n' >> "$PROFILE_FILE"
      layers=$((layers+1))
      err "[redact] 계층 $layers: $d/$REDACT.txt"
    fi
  done
  if [ "$layers" -eq 0 ]; then
    err "redaction 프로파일을 찾을 수 없습니다: $REDACT.txt"
    err "  찾아본 곳: 플러그인 · \$AUTHORING_KIT_HOME/redact · 프로젝트 .claude/authoring/redact"
    err "개인정보가 든 글을 가리지 않은 채 외부로 보내지 않습니다 — 중단합니다."
    exit 3
  fi
  n=0
  while IFS=$'\t' read -r pat token; do
    case "$pat" in ''|'#'*) continue ;; esac
    [ -z "${token:-}" ] && continue
    if perl -0pi -e "s/$pat/$token/g" "$BODY_FILE" 2>/dev/null; then n=$((n+1)); fi
  done < "$PROFILE_FILE"
  REDACT_NOTE="(redaction: $REDACT, 계층 $layers개 · 규칙 $n개 적용)"
  err "[redact] 프로파일 '$REDACT' 적용 — 계층 $layers개 · 규칙 $n개. 원문은 전송하지 않습니다."
fi
ARTICLE_BODY="$(cat "$BODY_FILE")"

# ── 검토 축 — 글 종류마다 다르므로 파일에서 읽는다 ────────────────────────
if [ -n "$AXES_FILE" ] && [ ! -r "$AXES_FILE" ] && [ -r "$PLUGIN/skills/authoring-method/assets/$AXES_FILE" ]; then
  AXES_FILE="$PLUGIN/skills/authoring-method/assets/$AXES_FILE"
fi
if [ -n "$AXES_FILE" ] && [ -r "$AXES_FILE" ]; then
  AXES_TEXT="$(cat "$AXES_FILE")"
else
  [ -n "$AXES_FILE" ] && err "[warn] 축 파일을 읽을 수 없어 범용 축을 씁니다: $AXES_FILE"
  AXES_TEXT='1) 누락/생략: 이 글의 목적을 달성하는 데 꼭 필요한데 빠진 내용. "여기는 더 들어가야 한다"는 곳을 구체적으로.
2) 모순/충돌: 앞뒤가 어긋나는 서술, 정의와 사용이 다른 용어, 그림·표와 본문의 불일치.
3) 사실 정확성/시대성: 틀렸거나 낡은 설명, 근거가 약한 단정, 검증되지 않은 수치.'
fi

SYSTEM_PROMPT='너는 깐깐한 문서 검토자다. 주어진 글의 약점을 한국어로 지적하라.'
USER_PROMPT="다음 글을 검토해 줘. 아래 세 축을 중심으로, 가장 중요한 지적부터 항목별 bullet로 한국어로 답해 줘.

${AXES_TEXT}

동의하는 부분은 길게 칭찬하지 말고 한 줄로만 인정해 줘. 추측이 섞인 지적은 \"추정\"이라고 표시해 줘.

=== DOCUMENT ===
${ARTICLE_BODY}"

COMBINED_PROMPT="${SYSTEM_PROMPT}

${USER_PROMPT}"

CODEX_LAST="$TMP_DIR/codex.last"
CODEX_LOG="$TMP_DIR/codex.log"
CODEX_ERR="$TMP_DIR/codex.err"
AGY_OUT="$TMP_DIR/agy.out"
AGY_ERR="$TMP_DIR/agy.err"

call_codex() {
  if ! command -v codex >/dev/null 2>&1; then
    printf 'codex CLI 미설치 — ChatGPT 검토를 건너뜁니다.\n' >"$CODEX_ERR"
    return 0
  fi
  local model_args=()
  [ -n "$CODEX_MODEL" ] && model_args=(-m "$CODEX_MODEL")
  # API 키 미사용 — codex가 ChatGPT 로그인만 쓰도록 이 서브셸 한정으로 제거.
  unset OPENAI_API_KEY
  # read-only 샌드박스 + 작업 루트를 임시 디렉토리로 고정해 로컬 파일을 못 건드리게.
  if ! printf '%s' "$COMBINED_PROMPT" | run_limited codex exec \
        --skip-git-repo-check -s read-only --color never \
        -C "$TMP_DIR" -o "$CODEX_LAST" "${model_args[@]+"${model_args[@]}"}" - \
        >"$CODEX_LOG" 2>&1; then
    {
      printf 'codex 실행 실패 — 인증 만료(세션 종료)일 수 있습니다. `codex login` 후 다시 시도하세요.\n'
      grep -aiE 'ERROR:|unauthorized|log in again|invalidated|session has ended' "$CODEX_LOG" 2>/dev/null \
        | awk '!seen[$0]++' | tail -n 4
    } >"$CODEX_ERR"
    : >"$CODEX_LAST"
  fi
}

call_agy() {
  if ! command -v agy >/dev/null 2>&1; then
    printf 'antigravity CLI(agy) 미설치 — Gemini 검토를 건너뜁니다.\n' >"$AGY_ERR"
    return 0
  fi
  local model_args=()
  [ -n "$AGY_MODEL" ] && model_args=(-m "$AGY_MODEL")
  run_limited agy -p "$COMBINED_PROMPT" "${model_args[@]+"${model_args[@]}"}" \
    </dev/null >"$AGY_OUT" 2>"$AGY_ERR"
  local rc=$?
  if [ "$rc" -ne 0 ] || grep -qiE 'Authentication required|authentication timed out' "$AGY_OUT" 2>/dev/null; then
    cat "$AGY_OUT" >>"$AGY_ERR" 2>/dev/null
    printf '\nagy 인증 필요 — 터미널에서 `agy`를 한 번 실행해 Google 로그인 후 다시 시도하세요.\n' >>"$AGY_ERR"
    : >"$AGY_OUT"
  fi
}

call_codex &
PID_CODEX=$!
call_agy &
PID_AGY=$!
wait "$PID_CODEX" "$PID_AGY"

ANY_OUTPUT=0

printf '=== ChatGPT (codex CLI) ===\n'
if [ -s "$CODEX_LAST" ]; then
  cat "$CODEX_LAST"; printf '\n'; ANY_OUTPUT=1
elif [ -s "$CODEX_ERR" ]; then
  printf '[skip] %s\n' "$(cat "$CODEX_ERR")"
else
  printf '[빈 응답]\n'
fi

printf '\n=== Gemini (antigravity CLI) ===\n'
if [ -s "$AGY_OUT" ]; then
  cat "$AGY_OUT"; printf '\n'; ANY_OUTPUT=1
elif [ -s "$AGY_ERR" ]; then
  printf '[skip] %s\n' "$(cat "$AGY_ERR")"
else
  printf '[빈 응답]\n'
fi

if [ "$ANY_OUTPUT" -eq 0 ]; then
  err ""
  err "두 모델 모두 응답을 받지 못했습니다 — 외부 검토 미실시."
  if [ "$POLICY" = "warn" ]; then
    err "policy=warn 이라 진행합니다. **검토를 받은 것으로 치지 마세요** — 보고에 그대로 남기세요."
    exit 0
  fi
  err "policy=hard-fail — 이 글을 '완성'으로 간주하지 마세요."
  exit 2
fi

# 부분 성공은 진행하되 어느 쪽이 빠졌는지 반드시 남긴다. 조용히 한쪽만 받고
# "검토 완료"라고 보고하면, 나중에 왜 놓쳤는지 추적할 수 없다.
MISSING=""
[ -s "$CODEX_LAST" ] || MISSING="ChatGPT(codex)"
[ -s "$AGY_OUT" ] && : || MISSING="${MISSING:+$MISSING, }Gemini(agy)"
if [ -n "$MISSING" ]; then
  printf '\n[부분 성공] 응답 없음: %s — 보고에 이 사실을 남기세요.\n' "$MISSING"
fi
[ -n "$REDACT_NOTE" ] && printf '[전송 전 처리] %s\n' "$REDACT_NOTE"
exit 0
