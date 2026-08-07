# Validation Report

Validated on 2026-08-07 in the artifact build environment.

## Passed

- `gofmt` check for both Go applications
- `go test ./apps/harbor-observer/... ./apps/nsq-reliable-worker/...`
- `go vet ./apps/harbor-observer/... ./apps/nsq-reliable-worker/...`
- Harbor Observer smoke test with two local HTTP replicas
- NSQ Job API smoke test with a fake NSQ HTTP publisher
- Duplicate `Idempotency-Key` returned HTTP 409
- NSQ V2 protocol test covering magic bytes, `IDENTIFY`, `SUB`, `RDY`, heartbeat/`NOP`, message parsing, and `FIN`
- `compose.yaml` YAML parse
- JSON manifest parse
- Relative Markdown link validation
- TypeScript source check with the available compiler and a temporary declaration matching the documented PGlite API

## Not executed in this environment

The build environment cannot reach the npm registry, so `npm install` and the final Vite bundle were not executed. The frontend dependency names and versions were checked against the official repositories:

- `@electric-sql/pglite 0.5.4`
- `vite 8.2.1`
- `typescript 6.0.0`

Run the following after extraction to complete the frontend verification:

```bash
cd apps/pgplay-recipes
npm install
npm run typecheck
npm run build
```
