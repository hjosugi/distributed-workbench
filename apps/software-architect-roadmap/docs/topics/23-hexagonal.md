# 23. Hexagonal architecture

[All 53 topics](../ROADMAP.md) · 4. Architectural patterns · **Ports and adapters**

## Meaning and purpose

Hexagonal architecture keeps application rules inside a boundary and connects external systems through ports and adapters. The important idea is dependency direction, not a six-sided drawing or six services.

## How the example works

OrderRepository is an outbound port owned near the core. SqliteOrders and MemoryOrders are adapters. HTTP and the CLI are inbound adapters. place_order receives a repository instead of constructing one, making adapter replacement explicit and testable.

Implementation: [architect_lab/domain.py](../../architect_lab/domain.py), [architect_lab/storage.py](../../architect_lab/storage.py), [tests/test_core.py](../../tests/test_core.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab orders
```

Expected result: The same use case succeeds with SQLite and memory. Contract tests verify common request identity and conflict behavior.

## Tradeoffs and failure cases

An interface for every function adds noise. Choose ports at meaningful boundaries such as persistence, time, or a payment provider. Adapter substitution must preserve required semantics; a memory adapter does not prove durability.

## Practice and interview discussion

Introduce a clock port only when time affects a business rule. Explain why the core should not import the database adapter. Interview phrase: The core defines the contract, and infrastructure implements it.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://alistair.cockburn.us/hexagonal-architecture/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
