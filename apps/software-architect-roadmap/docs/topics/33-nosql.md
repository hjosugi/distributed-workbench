# 33. NoSQL

[All 53 topics](../ROADMAP.md) · 6. Data and analytics · **Document model plus real Redis profile**

## Meaning and purpose

NoSQL covers several non-relational models, including key-value, document, wide-column, and graph stores. It does not automatically mean no schema, no transactions, or eventual consistency; guarantees depend on the database and operation.

## How the example works

The local DocumentStore serializes JSON into immutable object versions and checks expected_version before replacement. Its ID index is intentionally process-local. The optional Redis profile provides a real key-value server with append-only persistence; use redis-cli for HSET, HGETALL, and EXPIRE.

Implementation: [architect_lab/data.py](../../architect_lab/data.py), [compose.yaml](../../compose.yaml).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab data
```

Expected result: The local demo reads the original JSON structure. Tests reject a stale expected version. The Redis commands in the integration guide store and retrieve a product hash.

## Tradeoffs and failure cases

The local class is a model, not a durable concurrent NoSQL database. Redis persistence, replication, expiration, and failover need separate configuration. Flexible documents still require validation and migration strategy.

## Practice and interview discussion

Design a product lookup key and decide whether writes need compare-and-set. Explain why database type alone does not determine consistency. Interview phrase: I choose the data model and guarantees for the access pattern.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://hub.docker.com/_/redis). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
