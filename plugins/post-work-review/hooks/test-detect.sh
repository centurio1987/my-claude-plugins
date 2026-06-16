#!/usr/bin/env bash
# test-detect.sh — detect-completion.sh 의 케이스별 자동 테스트.
# 사용법: bash test-detect.sh
# 각 케이스: 임시 디렉토리를 만들고 PLAN.md/BACKLOG.md 를 구성한 뒤 훅을 실행,
#           기대한 출력(emit 여부)과 exit 0 을 검증한다.

set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/detect-completion.sh"
pass=0; fail=0

run_case() {
  desc="$1"; expect="$2"; shift 2   # expect = emit | silent
  tmp=$(mktemp -d)
  ( cd "$tmp" && "$@" )             # $@ = setup function call writing files into $tmp
  out=$(cd "$tmp" && CLAUDE_PROJECT_DIR="$tmp" bash "$HOOK" </dev/null 2>/dev/null)
  rc=$?
  emitted=silent
  case "$out" in *systemMessage*) emitted=emit;; esac
  if [ "$rc" -ne 0 ]; then
    printf 'FAIL [%s] exit=%s (expected 0)\n' "$desc" "$rc"; fail=$((fail+1))
  elif [ "$emitted" != "$expect" ]; then
    printf 'FAIL [%s] got=%s expected=%s\n' "$desc" "$emitted" "$expect"; fail=$((fail+1))
  else
    printf 'PASS [%s] (%s, exit 0)\n' "$desc" "$emitted"; pass=$((pass+1))
  fi
  rm -rf "$tmp"
}

# --- 케이스 setup 함수들 (cwd = 임시 디렉토리) ---
c_incomplete() { printf -- '- [x] done\n- [ ] todo\n' > PLAN.md; }
c_complete()   { printf -- '- [x] a\n- [x] b\n' > PLAN.md; }
c_nofiles()    { : ; }
c_codeblock()  { printf -- '- [x] real\n```\n- [ ] inside code\n```\n' > PLAN.md; }
c_htmlcomment(){ printf -- '- [x] real\n<!-- - [ ] commented -->\n' > PLAN.md; }
c_variants()   { printf -- '* [X] star upper\n+ [x] plus lower\n  - [x] indented\n' > PLAN.md; }
c_no_checkbox(){ printf -- 'just prose, no checkboxes\n' > PLAN.md; }
c_split()      { printf -- '- [x] plan done\n' > PLAN.md; printf -- '- [ ] backlog left\n' > BACKLOG.md; }
c_both_done()  { printf -- '- [x] plan done\n' > PLAN.md; printf -- '- [x] backlog done\n' > BACKLOG.md; }

run_case "incomplete -> silent"            silent c_incomplete
run_case "all complete -> emit"            emit   c_complete
run_case "no files -> silent"              silent c_nofiles
run_case "checkbox in code block ignored"  emit   c_codeblock
run_case "checkbox in html comment ignored" emit  c_htmlcomment
run_case "bullet/case variants -> emit"    emit   c_variants
run_case "no checkbox file -> silent"      silent c_no_checkbox
run_case "PLAN done + BACKLOG left -> silent" silent c_split
run_case "both files complete -> emit"     emit   c_both_done

# 중복 제안 방지: 같은 상태에서 두 번째 실행은 silent.
tmp=$(mktemp -d)
( cd "$tmp" && printf -- '- [x] a\n' > PLAN.md )
first=$(cd "$tmp" && CLAUDE_PROJECT_DIR="$tmp" bash "$HOOK" </dev/null 2>/dev/null)
second=$(cd "$tmp" && CLAUDE_PROJECT_DIR="$tmp" bash "$HOOK" </dev/null 2>/dev/null)
case "$first" in *systemMessage*) f1=emit;; *) f1=silent;; esac
case "$second" in *systemMessage*) f2=emit;; *) f2=silent;; esac
if [ "$f1" = emit ] && [ "$f2" = silent ]; then
  printf 'PASS [dedup: first emit, second silent]\n'; pass=$((pass+1))
else
  printf 'FAIL [dedup] first=%s second=%s\n' "$f1" "$f2"; fail=$((fail+1))
fi
rm -rf "$tmp"

printf '\n=== %s passed, %s failed ===\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
