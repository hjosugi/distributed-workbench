# Validation Report

Validated on 2026-08-08.

## Static checks

- `gofmt` check for both Go applications
- `go test ./apps/harbor-observer/... ./apps/nsq-reliable-worker/...`
- `go vet ./apps/harbor-observer/... ./apps/nsq-reliable-worker/...`
- NSQ V2 protocol test covering magic bytes, `IDENTIFY`, `SUB`, `RDY`, heartbeat/`NOP`, message parsing, and `FIN`
- `npm ci`, `npm run typecheck`, and `npm run build` for PGPlay Recipes
- `compose.yaml` parse and `docker compose build` for all four images

## Live stack

`docker compose up -d` was run and every service answered on its published port:
Harbor Observer 8081, NSQ Job API 8082, worker metrics 8083, NSQ Admin 4171, PGPlay Recipes 5173.
The worker logged `consumer connected` against the real `nsqd` over raw NSQ V2.

### NSQ end-to-end

`scripts/demo-nsq.sh` submitted a success job, a job failing until attempt 2, and a job that
always fails. One already-processed job id was then republished straight to the `jobs` topic to
exercise redelivery. Worker metrics afterwards:

| metric | value | meaning |
| --- | --- | --- |
| `nsq_worker_received_total` | 10 | 1 success + 3 retry attempts + 5 DLQ attempts + 1 replay |
| `nsq_worker_processed_total` | 2 | success job and retry job (succeeded on attempt 3) |
| `nsq_worker_retries_total` | 6 | 2 requeues for the retry job, 4 for the DLQ job |
| `nsq_worker_dlq_total` | 1 | DLQ job after `MAX_ATTEMPTS=5` |
| `nsq_worker_duplicates_total` | 1 | replayed job skipped instead of reprocessed |
| `nsq_worker_errors_total` | 0 | |

`nsqd` confirmed the same picture independently: topic `jobs` channel `processor` reported
`requeue_count=6` with `depth=0` and `in_flight_count=0`, and topic `jobs_dlq` held 1 message.
A duplicate `Idempotency-Key` on the Job API returned HTTP 409.

### Harbor Observer end-to-end

Probed against two local HTTP replicas. All three summary states were reproduced, and the
three runs persisted to the history JSONL and came back from `GET /api/probes` newest first:

| scenario | `state` | `variant_count` |
| --- | --- | --- |
| replicas serve identical bytes | `healthy` | 1 |
| one replica's content changed | `divergent` | 2 |
| one replica down | `single-copy-risk` | 1 |

Input guards: an absolute URL and a protocol-relative `//host` path were both rejected with
HTTP 400, and an unknown JSON field was rejected by `DisallowUnknownFields`. A 9 MiB response
was cut to exactly 8388608 bytes with `truncated: true`, matching the `MAX_BODY_BYTES` default.

## Frontend dependency versions

Resolved against the npm registry:

- `@electric-sql/pglite 0.5.4`
- `vite 8.2.1`
- `typescript 7.0.2`

TypeScript has no stable `6.0.0` release — `6.0.0-beta` is the only 6.x tag, and the current
stable line is 7.x. `package-lock.json` is committed and both CI and the Dockerfile use `npm ci`.

## Not covered

- The PGlite WASM database was not driven through a real browser; the page is only verified to
  build and to be served by nginx.
- Harbor Observer was validated against plain HTTP replicas, not a real Harbor registry.

## Reproducing

```bash
./scripts/verify.sh     # gofmt, go test, go vet, and the frontend build when node_modules exists

docker compose up -d
./scripts/demo-nsq.sh
./scripts/demo-harbor.sh
curl -s http://localhost:8083/metrics | grep nsq_worker
```
