# 15. ACID

[All 53 topics](../ROADMAP.md) · 3. Design principles · **Real SQLite transaction and failure injection**

## Meaning and purpose

ACID means atomicity, consistency, isolation, and durability. Atomicity prevents partial transactions. Consistency preserves declared invariants. Isolation controls interactions between transactions. Durability retains committed data under the database and storage guarantees.

## How the example works

One SQLite transaction inserts the order and its outbox event. BEGIN IMMEDIATE serializes writers before checking the unique request key. A deliberate failure after the order insert triggers rollback. Closing and reopening the database demonstrates process-level persistence, while unique and CHECK constraints defend invariants.

Implementation: [architect_lab/storage.py](../../architect_lab/storage.py), [tests/test_core.py](../../tests/test_core.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab acid
```

Expected result: rows_after_failure=0, rows_after_reopen=1, and outbox=1. A 24-call concurrent retry test creates exactly one order.

## Tradeoffs and failure cases

This is not a power-loss durability test. SQLite write serialization limits throughput, and a transaction cannot atomically commit a remote payment API. ACID consistency refers to invariants, while CAP consistency refers to a distributed consistency model.

## Practice and interview discussion

Move the outbox insert outside the transaction in a disposable branch and observe the lost-event failure. Interview phrase: I commit the business row and the event record in the same transaction.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.python.org/3/library/sqlite3.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
