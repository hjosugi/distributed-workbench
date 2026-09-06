# Validation record

Date: 2026-09-06. These are execution results, not a production-readiness claim.

## Locally executed

| Check | Environment | Result |
|---|---|---|
| Python behavior tests | Python 3.12.13 | 34 tests passed, no skips |
| AES-GCM test | cryptography 46.0.0 | Roundtrip and associated-data rejection passed |
| Python, JavaScript, Java catalog contracts | Python 3.12, Node 24.19, OpenJDK 17.0.20 | All three passed |
| Node HTTP test | node:test | Passed |
| All 11 CLI labs | Python standard library | Completed |
| DNS, TCP, HTTPS | Loopback UDP/TCP, OpenSSL, Python ssl | Completed; wrong hostname rejected |
| Hadoop mapper/reducer | Real local subprocess pipeline | Fixture and empty input passed |
| Lambda handler | Local Python invocation | Valid fixture and invalid inputs passed |
| YAML and JSON parsing | PyYAML 6.0.3 | Passed |
| Topic inventory and internal Markdown links | check_docs.py | 53 topics mapped, links verified |

Important behavior tests include 24 concurrent retries producing one order, order/outbox rollback, consumer/inbox rollback, replay after a crash, stable accepted price after catalog changes, replay while Catalog is unavailable, late-event classification, migration replay, JWT tampering, and authorization-code replay rejection.

## CI verification

The parent [architect-roadmap workflow](../../../.github/workflows/architect-roadmap.yml) also defines Go tests, four-language HTTP contracts, Docker build, NGINX cache/bypass checks, real Kafka delivery, and Redis hash/expiration checks. A workflow file alone is not a passing result. Inspect the [Actions runs](https://github.com/hjosugi/distributed-workbench/actions/workflows/architect-roadmap.yml) for actual execution status.

## External systems not executed locally

Go and Docker are not installed in the authoring environment. Kubernetes/kind, HDFS/YARN, AWS/SAM containers, a Jenkins controller, Jira submission, and a SonarQube scan were not run. ELK configuration was parsed, but the services were not started locally. Their implementations, configurations, and prerequisites are supplied; runtime verification is not implied.

The repository requests `graphify update .` after edits. The graphify executable is unavailable in the authoring environment, and there was no existing graphify-out graph to update. No graph generation is claimed.

## Scope boundaries

- The Python HTTP server is a local teaching server without authentication.
- The Kafka broker is single-node and ephemeral; the outbox demo uses its own local dispatcher.
- The document store is a model with a process-local index, not a durable NoSQL server.
- The local cache is a CDN behavior model, not a geographic CDN deployment.
- CAP and event-log implementations are deterministic models, not consensus or replicated-log systems.
- The OAuth example begins after hypothetical login/consent. It is not a complete identity provider.
- The K8s manifest intentionally uses one replica and emptyDir storage.
- Local database reopen tests do not prove power-loss recovery or full production durability.
