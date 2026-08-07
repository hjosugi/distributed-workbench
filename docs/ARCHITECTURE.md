# Architecture

```text
Browser
  ├── Harbor Observer dashboard (:8081)
  │      └── configured Harbor servers
  │             ├── /status
  │             └── /blob/{digest}
  │
  ├── NSQ Job API (:8082)
  │      └── durable outbox
  │             └── nsqd HTTP publish (:4151)
  │
  ├── NSQ Admin (:4171)
  │
  └── PGPlay Recipes (:5173)
         └── PGlite WASM + IndexedDB

nsqd TCP (:4150)
  └── Reliable Worker
         ├── NSQ V2 protocol
         ├── processed JSONL
         ├── retry / REQ
         └── DLQ publish
```

## Production upgrade path

### Harbor Observer

- JSONL history -> PostgreSQL/TimescaleDB
- polling -> scheduled probes
- local dashboard -> auth + multi-tenant
- path probe -> generated Polycentric gRPC client
- single process -> queue-backed workers

### NSQ Worker

- JSONL outbox -> PostgreSQL transactional outbox
- processed JSONL -> unique `message_id` table in the business transaction
- one nsqd address -> nsqlookupd discovery
- local metrics -> Prometheus + Grafana
- simple DLQ -> replay UI and retention policy

### PGPlay Recipes

- textarea -> Monaco editor
- URL base64 -> compressed share document
- local recipes -> versioned team recipe registry
- manual schema refresh -> catalog diff and migration generator
