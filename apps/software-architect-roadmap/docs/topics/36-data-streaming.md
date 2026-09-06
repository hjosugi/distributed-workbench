# 36. Data Streaming

[All 53 topics](../ROADMAP.md) · 6. Data and analytics · **Event-time windows and late-data policy**

## Meaning and purpose

Stream processing computes continuously over arriving events. Processing time is when a worker sees data; event time is when the event happened. Out-of-order arrival makes window completion a policy decision.

## How the example works

The model groups quantity into 60-second tumbling windows. It advances a global watermark from the maximum observed event time minus five seconds. A record is dropped when its window end is at or behind that watermark. Final buckets are returned after the finite fixture is consumed.

Implementation: [architect_lab/distributed.py](../../architect_lab/distributed.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab streaming
```

Expected result: Events at 1,61,58,130,2 produce book counts 2,1,1 in windows 0,60,120. The final event at time 2 is classified as late.

## Tradeoffs and failure cases

This is a deterministic window model, not a distributed streaming engine. It retains buckets and has one global watermark. A real job needs state eviction, checkpoints, partition-aware watermarks, deduplication, and an explicit late-event destination.

## Practice and interview discussion

Increase allowed lateness and compare correctness, latency, and state size. Explain what happens when one source partition stops sending events. Interview phrase: I define a watermark and a policy for late events.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://kafka.apache.org/quickstart/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
