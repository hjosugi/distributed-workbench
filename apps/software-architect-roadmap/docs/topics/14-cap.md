# 14. CAP theorem

[All 53 topics](../ROADMAP.md) · 3. Design principles · **Deterministic partition model**

## Meaning and purpose

CAP concerns what happens during a network partition: a distributed read/write service cannot guarantee both linearizable consistency and a successful response to every request at every non-failed node. Partition tolerance is a failure condition to design for, not a feature to casually turn off.

## How the example works

The model splits a leader from an isolated replica. A write reaches the leader. In CP mode the isolated read is rejected; in AP mode it returns the old value. Healing copies the leader value. The example illustrates one operation and one failure; it does not implement quorum, election, or a consensus algorithm.

Implementation: [architect_lab/distributed.py](../../architect_lab/distributed.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab cap
```

Expected result: CP returns unavailable. AP returns 0 while the leader holds 42. After healing, both modes return 42.

## Tradeoffs and failure cases

Availability in CAP is not an uptime percentage or a promise of bounded latency. The model has one writer and does not resolve concurrent conflicting writes. Real systems may choose different behavior for inventory, catalog, and analytics operations.

## Practice and interview discussion

For stock reservation, decide whether to reject a request or risk overselling during a partition. For a recommendation feed, decide whether stale output is acceptable. Interview phrase: During a partition, I choose the behavior based on the operation.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
