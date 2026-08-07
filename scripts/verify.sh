#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

echo '==> checking gofmt'
unformatted=$(gofmt -l apps/harbor-observer apps/nsq-reliable-worker)
if [ -n "$unformatted" ]; then
  echo "$unformatted"
  echo 'Go files are not formatted.' >&2
  exit 1
fi

echo '==> running Go tests'
go test ./apps/harbor-observer/... ./apps/nsq-reliable-worker/...

echo '==> running Go vet'
go vet ./apps/harbor-observer/... ./apps/nsq-reliable-worker/...

if [ -d apps/pgplay-recipes/node_modules ]; then
  echo '==> checking PGPlay Recipes'
  (cd apps/pgplay-recipes && npm run typecheck && npm run build)
else
  echo '==> PGPlay Recipes skipped: node_modules is not installed'
fi
