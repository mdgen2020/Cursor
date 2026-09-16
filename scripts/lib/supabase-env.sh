#!/usr/bin/env bash
# Shared Supabase REST helpers for local demo scripts (not used by Genesys).

load_supabase_env() {
  local root="$1"
  if [[ -f "$root/.env" ]]; then
    # shellcheck disable=SC1091
    source "$root/.env"
  fi

  SUPABASE_URL="${SUPABASE_URL:-https://njjkupupxvfvymelcjpg.supabase.co}"

  if [[ -z "${SUPABASE_SECRET_KEY:-}" ]]; then
    echo "Set SUPABASE_SECRET_KEY in ${root}/.env (Supabase → Project Settings → API → secret key)." >&2
    echo "Copy from example: cp .env.example .env" >&2
    exit 1
  fi

  # Trim whitespace / accidental quotes from paste
  SUPABASE_SECRET_KEY="${SUPABASE_SECRET_KEY#"${SUPABASE_SECRET_KEY%%[![:space:]]*}"}"
  SUPABASE_SECRET_KEY="${SUPABASE_SECRET_KEY%"${SUPABASE_SECRET_KEY##*[![:space:]]}"}"
  SUPABASE_SECRET_KEY="${SUPABASE_SECRET_KEY#\"}"
  SUPABASE_SECRET_KEY="${SUPABASE_SECRET_KEY%\"}"

  if [[ "$SUPABASE_SECRET_KEY" == "sb_secret_..." ]] || [[ "$SUPABASE_SECRET_KEY" == *"your"* ]]; then
    echo "SUPABASE_SECRET_KEY in .env is still a placeholder." >&2
    echo "Use the real sb_secret_… key for project njjkupupxvfvymelcjpg (not sb_publishable_…)." >&2
    exit 1
  fi

  if [[ "$SUPABASE_SECRET_KEY" == sb_publishable_* ]]; then
    echo "SUPABASE_SECRET_KEY must be the secret key (sb_secret_…), not the publishable key." >&2
    exit 1
  fi

  SUPABASE_APIKEY="$SUPABASE_SECRET_KEY"
  SUPABASE_USE_BEARER=0
  if [[ "$SUPABASE_SECRET_KEY" == eyJ* ]]; then
    # Legacy service_role JWT: PostgREST expects apikey + Authorization Bearer
    SUPABASE_USE_BEARER=1
  fi
}

supabase_rpc() {
  local fn="$1"
  local body="$2"
  if [[ "$SUPABASE_USE_BEARER" == 1 ]]; then
    curl -sS -X POST "${SUPABASE_URL}/rest/v1/rpc/${fn}" \
      -H "apikey: ${SUPABASE_APIKEY}" \
      -H "Authorization: Bearer ${SUPABASE_APIKEY}" \
      -H "Content-Type: application/json" \
      -d "$body"
  else
    curl -sS -X POST "${SUPABASE_URL}/rest/v1/rpc/${fn}" \
      -H "apikey: ${SUPABASE_APIKEY}" \
      -H "Content-Type: application/json" \
      -d "$body"
  fi
}

check_supabase_api_error() {
  local json="$1"
  if echo "$json" | grep -q '"Invalid API key"'; then
    echo "" >&2
    echo "Supabase rejected the API key for: ${SUPABASE_URL}" >&2
    echo "  • URL and secret must be from the SAME project (Dashboard → Settings → API)." >&2
    echo "  • Use the secret key (sb_secret_…), not publishable." >&2
    echo "  • Canonical demo project: njjkupupxvfvymelcjpg (URL and secret must match)." >&2
    exit 1
  fi
}
