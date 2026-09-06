# 20. Event-Driven Architecture / EDA

[All 53 topics](../ROADMAP.md) · 4. Architectural patterns · **Transactional outbox and inbox**

## Meaning and purpose

Event-driven architecture uses events to trigger behavior and update derived state. An event describes a fact that already happened. A command asks a specific owner to perform an action; these are different contracts.

## How the example works

Order creation atomically records OrderPlaced in an outbox. A dispatcher sends it to two consumer projections. Each consumer stores its event ID and revenue update in the same SQLite transaction. If the dispatcher crashes before marking delivery, replay reaches the inbox and does not add revenue again.

Implementation: [architect_lab/storage.py](../../architect_lab/storage.py), [tests/test_core.py](../../tests/test_core.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab events
```

Expected result: Both consumer totals remain 3000 after injected failure and replay. Pending outbox records reach zero after successful dispatch.

## Tradeoffs and failure cases

The dispatcher is local and synchronous, and each projection is simplified to a total. Its atomic inbox guarantee applies to the same database transaction; it cannot make an external email or payment exactly once. Production outbox relays need leases, retries, monitoring, and poison-event handling.

## Practice and interview discussion

Add version 2 of an event while keeping a version-1 consumer working. Define schema compatibility and replay policy. Interview phrase: I accept duplicate delivery and make the business effect idempotent.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://kafka.apache.org/quickstart/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
