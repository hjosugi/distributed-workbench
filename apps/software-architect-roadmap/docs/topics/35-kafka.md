# 35. Kafka

[All 53 topics](../ROADMAP.md) · 6. Data and analytics · **Real broker and producer/consumer integration**

## Meaning and purpose

Kafka stores durable ordered logs split into partitions. Consumers pull records and track offsets. Ordering is within a partition; multiple consumer groups can independently read the same topic.

## How the example works

The profile runs the official Kafka image in single-node KRaft mode. The roundtrip script creates a unique one-partition topic, publishes three JSON events with the official console producer, and consumes them through two groups. It verifies the payload and cleans up only its own temporary topic.

Implementation: [compose.yaml](../../compose.yaml), [scripts/kafka_roundtrip.py](../../scripts/kafka_roundtrip.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
docker compose --profile data up -d kafka redis
```

Expected result: After Kafka is healthy, python3 scripts/kafka_roundtrip.py prints a passing publish/consume result. Both groups see the same ordered fixture.

## Tradeoffs and failure cases

The lab has replication factor 1 and loses broker data on container replacement. It is not a highly available Kafka deployment. Exactly-once stream processing does not automatically make external database or HTTP effects exactly once.

## Practice and interview discussion

Choose an event key for per-order ordering, then explain the relationship between partitions and active consumers in one group. Interview phrase: I use the order ID as the key to keep related events ordered.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://kafka.apache.org/quickstart/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
