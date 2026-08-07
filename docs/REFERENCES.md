# References and dependency choices

## Harbor / Polycentric

- Documentation: https://docs.polycentric.io/
- Source: https://gitlab.futo.org/polycentric/polycentric
- GitHub mirror used during investigation: https://github.com/futo-org/Harbor

Harbor server exposes plain HTTP routes such as `/status` and `/blob/{digest}` alongside gRPC/gRPC-Web. Harbor Observer intentionally starts with the HTTP surface because it is useful without generated protocol bindings and works for content hash comparison.

## NSQ

- Official project: https://github.com/nsqio/nsq
- Documentation: https://nsq.io/
- Docker image pinned by this sample: `nsqio/nsq:v1.3.0`

The official NSQ repository was still receiving updates in July 2026. The `harporoeder/tokio-nsq` client is not used here: its repository version is `0.14.0`, its latest observed commit is from June 2023, and its manifest still contains older `rustls`/`tokio-rustls` dependencies. Instead, this sample implements the small NSQ V2 subset it needs with the Go standard library.

`harporoeder` is the maintainer's username and is unrelated to FUTO's Harbor product.

## PGlite

- Official project: https://github.com/electric-sql/pglite
- Documentation: https://pglite.dev/
- Version pinned by this sample: `@electric-sql/pglite 0.5.4`

PGlite supports `idb://` browser storage and `PGlite.create()`. PGPlay Recipes uses both, so the database survives browser reloads without a separate PostgreSQL container.

## pgplay inspiration

- Repository: https://github.com/Taha-Firoz/pgplay

This monorepo does not copy pgplay. It adopts the useful idea of removing temporary database setup, then narrows the product around distributed-systems schemas and operational recipes.

## Build tooling

- Vite `8.2.1` from the official `vitejs/vite` package manifest.
- TypeScript `6.0.0` from the official `microsoft/TypeScript` package manifest.
- Node.js 24 is used by the Docker and CI definitions.
