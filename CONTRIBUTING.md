# Contributing

## Local checks

```bash
make fmt
make test
```

For the browser app:

```bash
cd apps/pgplay-recipes
npm install
npm run typecheck
npm run build
```

## Repository rule

Keep each app independently runnable. Shared documentation belongs under `docs/`; app-specific commands and environment variables belong in that app's README.

## Commit scope examples

- `harbor: add scheduled probe endpoint`
- `nsq: persist DLQ replay state`
- `pgplay: add index recommendation check`
- `docs: clarify production upgrade path`
