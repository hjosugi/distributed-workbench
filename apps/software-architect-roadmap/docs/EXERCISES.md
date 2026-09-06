# Learning path and failure exercises

Start from the module README. Read one topic, run its command, change one condition, and explain the result in plain English.

## Suggested order

| Session | Read | Run | Explain without notes |
|---|---|---|---|
| 1 | Languages, OOP, Clean Code | orders, catalog contracts | Boundary validation and integer money |
| 2 | TDD, DDD, ACID, MVC | acid and HTTP tests | Transaction boundaries and accepted prices |
| 3 | Layered, Hexagonal, GoF | orders, gof | Dependency direction and one useful pattern |
| 4 | Client-Server, Microservices | two-service HTTP test | Timeout ambiguity and safe retries |
| 5 | Pub/Sub, EDA, Kafka | events, Kafka roundtrip | Delivery versus business effect |
| 6 | CAP, Distributed Systems | cap, distributed | Partition behavior and key movement |
| 7 | SQL, NoSQL, Hadoop, OLAP | data and mapper/reducer | Access patterns and aggregation |
| 8 | Streaming, Object Storage, Migration | streaming, migration | Late data and schema compatibility |
| 9 | Networking and Security | networking, security | Trust, framing, claims, code binding |
| 10 | Platform, Tools, Supporting Skills | Compose, planning | Operations, tradeoffs, and ownership |

This is a flexible learning sequence, not a claim that mastering architecture takes ten days. Use the topic guide's practice question before moving on.

## Failure injection

| Scenario | Existing evidence | Further exercise |
|---|---|---|
| Insert order then fail | Rollback test leaves no order/outbox | Move event insert outside transaction in a disposable branch |
| Consumer succeeds then relay crashes | Revenue remains 3000 after retry | Add a third independent consumer |
| 24 simultaneous retries | One order and one event | Compare different keys and observe write serialization |
| Catalog stops | New key gets 503; accepted key replays | Define a quote freshness policy |
| Isolated replica | CP rejects, AP reads stale | Add a concurrent-writer conflict policy |
| Window is closed | Late event is returned separately | Compare lateness settings |
| JWT payload changes | Signature verification fails | Add a key-rotation exercise using a maintained library |
| OAuth code reused | Second exchange fails | Draw a full browser state/PKCE flow |
| Object bytes corrupted | Checksum validation fails | Add a manifest and missing-object reconciliation |
| Migration reruns | One version record, old query works | Plan batched backfill for a large table |

## Completion checklist

For each topic, answer four questions: what problem does it solve, what does this implementation guarantee, what is outside its scope, and what failure test supports the claim? For interview rehearsal, use [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md). For the full source mapping, use [ROADMAP.md](ROADMAP.md).
