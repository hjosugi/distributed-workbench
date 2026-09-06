# 39. Data Migration

[All 53 topics](../ROADMAP.md) · 6. Data and analytics · **Idempotent expand/backfill example**

## Meaning and purpose

Data migration changes schema, data, or storage location while preserving meaning and service compatibility. Expand-and-contract introduces a compatible new representation before old readers and writers are removed.

## How the example works

The migration runs under a write transaction, checks schema_version, adds nullable currency, backfills existing orders with JPY, and records the version. Running it twice does not repeat the ALTER TABLE. Old queries continue to work.

Implementation: [architect_lab/storage.py](../../architect_lab/storage.py), [tests/test_core.py](../../tests/test_core.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab migration
```

Expected result: Existing orders have currency=JPY and the version table contains one row for version 1. Old list_orders output remains unchanged.

## Tradeoffs and failure cases

The fixture is small and uses a single backfill transaction. A production migration may need batches, resumable checkpoints, dual-read/write compatibility, throttling, and reconciliation. New writes must populate currency before making it NOT NULL; this lab intentionally stops at the expand/backfill stage.

## Practice and interview discussion

Describe the next deployment that writes currency, then the verification needed before adding a NOT NULL constraint. Interview phrase: I expand first, migrate data, switch clients, and contract last.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.python.org/3/library/sqlite3.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
