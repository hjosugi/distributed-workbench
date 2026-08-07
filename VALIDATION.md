# Validation Report

Validated on 2026-08-07.

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
- `npm install`, `npm run typecheck`, and `npm run build` for PGPlay Recipes

## Frontend dependency versions

Resolved against the npm registry:

- `@electric-sql/pglite 0.5.4`
- `vite 8.2.1`
- `typescript 7.0.2`

TypeScript has no stable `6.0.0` release — `6.0.0-beta` is the only 6.x tag, and the current stable line is 7.x. `package-lock.json` is committed so installs are reproducible.

## Reproducing

```bash
./scripts/verify.sh          # gofmt, go test, go vet, and the frontend build when node_modules exists

cd apps/pgplay-recipes
npm install
npm run typecheck
npm run build
```
