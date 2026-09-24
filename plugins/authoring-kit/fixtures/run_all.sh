#!/usr/bin/env bash
# authoring-kit 회귀 검사 전량. CI 에서도, 손으로도 같은 명령으로 돈다.
#
#   AUTHORING_KIT_HOME=<레지스트리> bash fixtures/run_all.sh [project_dir] [spec_id]
#
# 하나라도 실패하면 비-0 으로 죽는다. "통과했다"는 말은 이게 0으로 끝났다는 뜻이어야 한다.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN="$(dirname "$HERE")"
PROJECT="${1:-.}"
SPEC="${2:-algo-guide}"

fail=0
run() {
  echo
  echo "──────────────────────────────────────────────────────"
  echo "▶ $1"
  echo "──────────────────────────────────────────────────────"
  shift
  if ! "$@"; then fail=1; fi
}

run "층 분리 (요구사항 ①)"      python3 "$HERE/test_layer_separation.py"
run "명세 등록 왕복 (요구사항 ②)" python3 "$HERE/test_spec_roundtrip.py" "$PROJECT" "$SPEC"
run "플러그인 구조 · 컨텍스트 예산" python3 "$HERE/test_plugin_shape.py" "$PROJECT"
run "문체 스캐너 세는 단위"      python3 "$HERE/test_scanner.py"
run "린터 세는 단위"           python3 "$HERE/test_linter.py"
run "문체 설정 (계승·가중치·편집기)" python3 "$HERE/test_style.py"

echo
echo "──────────────────────────────────────────────────────"
echo "▶ 레지스트리 정합 (validate --all)"
echo "──────────────────────────────────────────────────────"
if ! python3 "$PLUGIN/scripts/authoring.py" validate --all --project "$PROJECT"; then fail=1; fi

echo
if [ "$fail" -eq 0 ]; then
  echo "전부 통과."
else
  echo "실패 있음."
fi
exit "$fail"
