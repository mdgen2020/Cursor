#!/usr/bin/env bash
# DOL_Front_Door_miked — local eval helper (prepare / score / open).
# Full Cicero runs: use Cursor Agent + ava-evaluate skill, or:
#   ./scripts/run-ava-eval-test-set.py cursor-prompt
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PY:-$ROOT/scripts/run-ava-eval-test-set.py}"
SLUG=dol-front-door-miked
TEST_SET=dol-front-door-miked-suite

cmd="${1:-help}"
shift || true

case "$cmd" in
  dry-run)
    exec "$PY" --slug "$SLUG" --test-set "$TEST_SET" dry-run "$@"
    ;;
  prepare)
    exec "$PY" --slug "$SLUG" --test-set "$TEST_SET" prepare "$@"
    ;;
  score)
    exec "$PY" --slug "$SLUG" score "$@"
    ;;
  open)
    exec "$PY" --slug "$SLUG" open "$@"
    ;;
  cursor-prompt)
    exec "$PY" --slug "$SLUG" --test-set "$TEST_SET" cursor-prompt "$@"
    ;;
  run)
    exec "$PY" --slug "$SLUG" --test-set "$TEST_SET" run "$@"
    ;;
  help|*)
    cat <<EOF
Usage: $0 <command> [args]

  dry-run       Show scenario count and projected Cicero calls
  prepare       Create next eval-runs/eval-run-YYYY-MM-DD-NNN/ + manifest
  score         --run-id <id>  Generate scorecard after scenario-runners finish
  open          --run-id <id>  Open scorecard.html in browser (macOS)
  cursor-prompt Print prompt to paste into Cursor for full eval
  run           Run scenarios via Cicero in terminal (--score-after to score)

Example workflow:
  $0 dry-run
  $0 prepare
  $0 run --run-id eval-run-2026-09-17-003 --score-after
  # Or after Cursor scenario-runners:
  $0 score --run-id eval-run-2026-09-17-002
  $0 open --run-id eval-run-2026-09-17-002

Reports live under:
  $ROOT/.ava-lifecycle/$SLUG/eval-runs/<run-id>/scorecard.html
EOF
    ;;
esac
