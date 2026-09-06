# 19. Publish Subscribe

[All 53 topics](../ROADMAP.md) · 4. Architectural patterns · **Consumer-offset model and Kafka integration**

## Meaning and purpose

Publish-subscribe sends an event to interested subscribers without coupling the publisher to each subscriber implementation. Independent subscriptions each receive events; workers in one consumer group typically divide work rather than each receiving every message.

## How the example works

EventLog appends records and keeps independent next offsets for analytics and billing. Polling without committing repeats data. The Kafka integration publishes fixture events to a one-partition topic and reads them through two independent groups.

Implementation: [architect_lab/distributed.py](../../architect_lab/distributed.py), [scripts/kafka_roundtrip.py](../../scripts/kafka_roundtrip.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab events
```

Expected result: After analytics commits offset 1, it has no pending event while billing still sees the record. The real Kafka script verifies both groups receive the fixture in order.

## Tradeoffs and failure cases

The in-memory log has no durability, replication, or rebalance support. A consumer offset is not the same as a business side-effect transaction. At-least-once delivery requires an idempotent consumer.

## Practice and interview discussion

Crash after a side effect but before an offset commit. Explain why an inbox or deduplication key prevents repeated effects. Interview phrase: Each subscriber tracks progress independently.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://kafka.apache.org/quickstart/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
