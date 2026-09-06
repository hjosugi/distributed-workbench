# 37. OLAP

[All 53 topics](../ROADMAP.md) · 6. Data and analytics · **Star-schema aggregation**

## Meaning and purpose

OLAP supports analytical queries across many records and dimensions, while OLTP focuses on short operational transactions. A star schema separates facts such as sales from dimensions such as products and time.

## How the example works

The sales table stores quantities and amounts; products supplies the category dimension. A join and GROUP BY compute category revenue. UNION ALL adds a grand total, making the relation between detail rows and aggregate output explicit.

Implementation: [architect_lab/data.py](../../architect_lab/data.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab data
```

Expected result: The fixture reports learning=3600, stationery=600, and ALL=4200. All totals come from SQL over real SQLite tables.

## Tradeoffs and failure cases

This demonstrates analytical modeling in SQLite, not a columnar warehouse benchmark. Large scans can compete with operational writes. Separate analytical storage, materialized views, or incremental projections may be appropriate at scale.

## Practice and interview discussion

Add a day dimension and explain double counting when facts join a dimension with duplicate keys. Interview phrase: I separate operational writes from large analytical scans when the workload requires it.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.python.org/3/library/sqlite3.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
