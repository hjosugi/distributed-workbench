# 13. Domain-Driven Design

[All 53 topics](../ROADMAP.md) · 3. Design principles · **Domain model and context boundary exercise**

## Meaning and purpose

DDD aligns software boundaries and language with business concepts. An entity has identity, a value object is defined by values, and an aggregate protects a consistency boundary. A bounded context owns a model and its meaning.

## How the example works

The order has an ID; Line is a value object. Ordering owns the accepted price snapshot and request identity. Catalog owns current product prices. Reporting consumes OrderPlaced facts and builds a separate projection. A later catalog price change does not change the total of an accepted order.

Implementation: [architect_lab/domain.py](../../architect_lab/domain.py), [architect_lab/storage.py](../../architect_lab/storage.py), [docs/SYSTEM_DESIGN.md](../../docs/SYSTEM_DESIGN.md).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab orders
```

Expected result: The order demo returns an ID and total. The price-change retry test returns the original total, showing that an order is a business record rather than a live view of catalog data.

## Tradeoffs and failure cases

DDD is not a rule to create one service per entity. A bounded context may start as a module. This lab omits stock reservations, payment authorization, fulfillment, and tax rules; adding them requires explicit business invariants.

## Practice and interview discussion

Define separate meanings of product in Catalog and Fulfillment, then write the event that crosses the boundary. Interview phrase: I choose boundaries around business ownership and consistency requirements.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://www.domainlanguage.com/ddd/reference/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
