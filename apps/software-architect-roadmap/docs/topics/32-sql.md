# 32. SQL

[All 53 topics](../ROADMAP.md) · 6. Data and analytics · **SQLite schema, transaction, index, and query plan**

## Meaning and purpose

SQL expresses relational queries over structured data. Tables, keys, constraints, joins, and transactions help preserve relationships. Choose access patterns and invariants before adding indexes.

## How the example works

The order schema has unique request identity and an outbox foreign key. Parameter placeholders bind values safely. The analytics fixture joins sales to products, groups revenue by category, and shows EXPLAIN QUERY PLAN for an indexed SKU lookup.

Implementation: [architect_lab/storage.py](../../architect_lab/storage.py), [architect_lab/data.py](../../architect_lab/data.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab data
```

Expected result: Learning revenue is 3600, stationery is 600, and total is 4200. The query plan identifies the SKU index.

## Tradeoffs and failure cases

An index increases write and storage cost. Small fixtures do not prove production performance. SQLite has different concurrency and operational characteristics from a server database such as PostgreSQL.

## Practice and interview discussion

Compare a point lookup and a category aggregation, then propose indexes for each. Interview phrase: I choose indexes from real query patterns and verify the query plan.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.python.org/3/library/sqlite3.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
