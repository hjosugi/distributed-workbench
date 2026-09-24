# Changelog

## 0.2.0 - 2026-09-24

- Added the software architect roadmap: 53 topics with executable labs, Python/JavaScript/Java/Go catalog APIs, and container checks (`apps/software-architect-roadmap`).
- Added a local realtime speech prompter with Vosk, Ollama and WebSocket streaming, including a model-free demo (`apps/realtime-prompter`).
- Fixed the documented Harbor Observer body limit (8 MiB) and made pgplay-recipes container builds use the committed lockfile.
- Bumped cryptography from 46.0.0 to 50.0.0 in the roadmap security requirements.

## 0.1.0 - 2026-08-07

- Added Harbor multi-server response and SHA-256 observer.
- Added NSQ durable outbox, raw V2 consumer, retry, idempotency, DLQ, and metrics.
- Added PGlite browser workbench with distributed-systems recipes.
- Added one Docker Compose entry point and CI definitions.
