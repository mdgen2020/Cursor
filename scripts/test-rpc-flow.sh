#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/lib/supabase-env.sh"
load_supabase_env "$ROOT"

rpc() {
  supabase_rpc "$1" "$2"
}

echo "== resident_verify =="
VERIFY_JSON="$(rpc resident_verify '{"p_first_name":"Linus","p_last_name":"Turing","p_date_of_birth":"1988-06-23"}')"
echo "$VERIFY_JSON" | (command -v jq >/dev/null && jq . || cat)
check_supabase_api_error "$VERIFY_JSON"

TOKEN=""
if command -v jq >/dev/null; then
  TOKEN="$(echo "$VERIFY_JSON" | jq -r '.session_token // empty')"
else
  TOKEN="$(echo "$VERIFY_JSON" | sed -n 's/.*"session_token"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
fi
if [[ -z "$TOKEN" ]]; then
  echo "No session_token in response (see above)." >&2
  exit 1
fi

echo ""
echo "== dta_case_status =="
CASE_JSON="$(rpc dta_case_status "{\"p_case_number\":\"SNAP-MA-100234\",\"p_session_token\":\"${TOKEN}\"}")"
echo "$CASE_JSON" | (command -v jq >/dev/null && jq . || cat)
check_supabase_api_error "$CASE_JSON"

echo ""
echo "== masshealth_screening_result =="
MH_JSON="$(rpc masshealth_screening_result "{\"p_session_token\":\"${TOKEN}\"}")"
echo "$MH_JSON" | (command -v jq >/dev/null && jq . || cat)
check_supabase_api_error "$MH_JSON"

echo ""
