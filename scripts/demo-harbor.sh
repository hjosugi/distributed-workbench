#!/usr/bin/env sh
set -eu

OBSERVER_URL="${OBSERVER_URL:-http://localhost:8081}"
PATH_TO_PROBE="${1:-/status}"

curl -fsS "$OBSERVER_URL/api/probes" \
  -H 'content-type: application/json' \
  -d "{\"path\":\"$PATH_TO_PROBE\"}"
printf '\n'
