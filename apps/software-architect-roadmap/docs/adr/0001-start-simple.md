# ADR 0001: Start with a small transactional core

Status: accepted for this learning module. Date: 2026-09-06.

## Context

We need all 53 roadmap topics to be inspectable on a local machine. A learner should be able to reproduce an order retry, transaction rollback, and repeated event delivery without running a cloud account or a cluster. The main correctness requirements are stable accepted-order identity and atomic order/outbox persistence.

## Decision

Use Python with SQLite for the core, a small repository port, and deterministic failure injection. Add separate four-language Catalog implementations and opt-in infrastructure profiles. Keep real service integrations and simplified models explicitly labeled.

## Alternatives

| Option | Advantages | Costs |
|---|---|---|
| Full microservice platform | More realistic service operations | Many prerequisites obscure the failure mechanism |
| Pure in-memory simulation | Fastest startup | Cannot demonstrate durable restart and transactions |
| Transactional local core | Real SQL and restart, simple setup | Limited concurrency and no shared cluster state |

## Consequences

The first command works with Python alone. HTTP, domain, and SQL stay separate. Production authentication, payment, durable broker operation, and multi-region recovery are not implied. Configuration-only integrations need their external runtimes.

## Revisit criteria

Revisit when a lesson requires concurrent independent deployments, persistent multi-node storage, provider-specific behavior, or measured throughput beyond the single-writer database. Preserve the same behavior tests while changing adapters. Record a new ADR rather than erasing this decision.
