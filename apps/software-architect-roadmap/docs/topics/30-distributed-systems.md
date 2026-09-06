# 30. Distributed Systems

[All 53 topics](../ROADMAP.md) · 5. Platform knowledge · **Hashing, partitions, retries, and delivery models**

## Meaning and purpose

A distributed system must work with independent processes, partial failures, delayed messages, and imperfect knowledge. A network call can time out even after its side effect has committed. Correctness needs explicit invariants and recovery rules.

## How the example works

The consistent-hash ring hashes nodes with virtual points and assigns a key to the next point clockwise. Adding node d moves only keys newly owned by d. The other labs demonstrate stale replicas, retry identity, and duplicate event delivery.

Implementation: [architect_lab/distributed.py](../../architect_lab/distributed.py), [architect_lab/storage.py](../../architect_lab/storage.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab distributed
```

Expected result: Only a subset of 1000 keys moves after adding one node. The test verifies every moved key belongs to the new node and stable keys keep their owners.

## Tradeoffs and failure cases

This ring has no replication, membership protocol, or live rebalancing. Virtual nodes improve distribution but do not automatically handle hot keys. Quorum intersection alone does not establish full linearizability without additional protocol assumptions.

## Practice and interview discussion

Explain what happens to in-flight writes during a shard move and how a hot product can overload one shard. Interview phrase: I design for partial failure and define ownership during changes.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
