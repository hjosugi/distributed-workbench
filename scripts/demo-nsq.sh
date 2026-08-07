#!/usr/bin/env sh
set -eu

API_URL="${API_URL:-http://localhost:8082}"

post_job() {
  key="$1"
  body="$2"
  printf '\n==> %s\n' "$key"
  curl -fsS "$API_URL/jobs" \
    -H 'content-type: application/json' \
    -H "Idempotency-Key: $key" \
    -d "$body"
  printf '\n'
}

post_job demo-success-001 '{"type":"success","payload":{"message":"first delivery succeeds"},"work_ms":100}'
post_job demo-retry-001 '{"type":"retry","payload":{"message":"succeeds on attempt 3"},"fail_until_attempt":2,"work_ms":100}'
post_job demo-dlq-001 '{"type":"dlq","payload":{"message":"exceeds max attempts"},"fail_until_attempt":100}'

printf '\nOpen NSQ Admin: http://localhost:4171\n'
printf 'Worker metrics:  http://localhost:8083/metrics\n'
