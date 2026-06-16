#!/usr/bin/env bash
# detect-completion.sh — post-work-review 플러그인의 Stop 훅.
#
# PLAN.md / BACKLOG.md 의 체크리스트가 "모두 완료"된 순간에 한 번만,
# 사용자에게 사후 작업 검토(/post-work-review)를 환기하는 systemMessage 를 출력한다.
#
# 원칙: 어떤 상황에서도 작업 흐름을 깨지 않도록 항상 exit 0.
#   - 트리거 조건: 체크박스를 가진 PLAN/BACKLOG 파일이 "모두" 완료(미완료 0개, 완료 1개 이상)일 때만.
#   - 한 파일이라도 미완료 항목이 남아 있으면 제안하지 않는다.
#   - fenced code block(``` / ~~~) 과 HTML 주석(<!-- -->) 안의 체크박스는 무시한다.
#   - 동일 상태(파일 내용 + git HEAD/diff)에서는 재제안하지 않는다.

set -u

# Stop 훅이 stdin 으로 넘기는 페이로드를 비우되, 없어도 멈추지 않는다.
if [ ! -t 0 ]; then cat >/dev/null 2>&1 || true; fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
cd "$PROJECT_DIR" 2>/dev/null || exit 0

# --- 체크박스 카운트 (코드펜스/HTML 주석 제외) ---
count_awk='
BEGIN { incode=0; incomment=0; unchecked=0; checked=0 }
{
  line=$0; sub(/\r$/,"",line)
  t=line; sub(/^[ \t]+/,"",t)
  if (incode==0 && t ~ /^(```|~~~)/) { incode=1; next }
  else if (incode==1 && t ~ /^(```|~~~)/) { incode=0; next }
  if (incode==1) next

  out=""; rest=line
  while (1) {
    if (incomment==1) {
      p=index(rest,"-->")
      if (p==0) { rest=""; break }
      rest=substr(rest,p+3); incomment=0
    }
    s=index(rest,"<!--")
    if (s==0) { out=out rest; break }
    out=out substr(rest,1,s-1)
    rest=substr(rest,s+4); incomment=1
  }
  line=out

  if (line ~ /^[ \t]*[-*+][ \t]+\[[ ]\]/) unchecked++
  else if (line ~ /^[ \t]*[-*+][ \t]+\[[xX]\]/) checked++
}
END { print unchecked" "checked }
'

any_file=0
has_any_checkbox=0
all_complete=1
for f in PLAN.md BACKLOG.md; do
  [ -f "$f" ] || continue
  any_file=1
  res=$(awk "$count_awk" "$f" 2>/dev/null) || res="0 0"
  u=${res% *}; c=${res#* }
  [ -n "$u" ] || u=0
  [ -n "$c" ] || c=0
  # 체크박스가 전혀 없는 파일은 판정에서 제외.
  if [ "$u" -eq 0 ] && [ "$c" -eq 0 ]; then continue; fi
  has_any_checkbox=1
  # 미완료가 남아 있거나, 완료가 0개면 "완료 아님".
  if [ "$u" -ne 0 ] || [ "$c" -eq 0 ]; then all_complete=0; fi
done

[ "$any_file" -eq 1 ]       || exit 0
[ "$has_any_checkbox" -eq 1 ] || exit 0
[ "$all_complete" -eq 1 ]   || exit 0

# --- 상태 키 (파일 내용 + git HEAD/diff) ---
git_part=""
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  head=$(git rev-parse HEAD 2>/dev/null || true)
  stat=$(git diff --stat 2>/dev/null || true)
  git_part="${head}
${stat}"
fi

if command -v shasum >/dev/null 2>&1; then HASHER="shasum -a 256"
elif command -v sha256sum >/dev/null 2>&1; then HASHER="sha256sum"
elif command -v cksum >/dev/null 2>&1; then HASHER="cksum"
else HASHER="cat"
fi

key=$({ cat PLAN.md BACKLOG.md 2>/dev/null; printf '%s' "$git_part"; } | $HASHER 2>/dev/null | awk '{print $1; exit}')
[ -n "$key" ] || key="present"

STATE_DIR=".claude"
STATE_FILE="$STATE_DIR/.post-work-review-state"

# 동일 상태면 재제안하지 않음.
if [ -f "$STATE_FILE" ]; then
  prev=$(cat "$STATE_FILE" 2>/dev/null || true)
  [ "$prev" = "$key" ] && exit 0
fi

# 상태 기록 (실패해도 무시).
mkdir -p "$STATE_DIR" 2>/dev/null || true
if [ -d "$STATE_DIR" ] && [ -w "$STATE_DIR" ]; then
  printf '%s' "$key" > "$STATE_FILE" 2>/dev/null || true
fi

# git 레포면 상태파일을 추적에서 제외 (레포를 더럽히지 않음).
if [ -f ".git/info/exclude" ]; then
  if ! grep -qxF ".claude/.post-work-review-state" ".git/info/exclude" 2>/dev/null; then
    printf '%s\n' ".claude/.post-work-review-state" >> ".git/info/exclude" 2>/dev/null || true
  fi
fi

printf '{"systemMessage":"PLAN/BACKLOG 체크리스트가 모두 완료되었습니다. /post-work-review 로 사후 작업(스킬·룰·에이전트 후보)을 점검하세요."}\n'
exit 0
