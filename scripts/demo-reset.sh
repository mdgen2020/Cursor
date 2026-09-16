#!/usr/bin/env bash
set -euo pipefail

SCENARIO="${1:-all}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/lib/supabase-env.sh"
load_supabase_env "$ROOT"

EOHHS_DEMO_RESET_KEY="${EOHHS_DEMO_RESET_KEY:-eohhs-demo-reset}"

OUT="$(supabase_rpc demo_reset_scenario "{\"p_scenario\":\"${SCENARIO}\",\"p_reset_key\":\"${EOHHS_DEMO_RESET_KEY}\"}")"
echo "$OUT" | (command -v jq >/dev/null && jq . || cat)
check_supabase_api_error "$OUT"
echo ""
