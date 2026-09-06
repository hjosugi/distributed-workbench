# 10. OOPS / Object-oriented programming

[All 53 topics](../ROADMAP.md) · 3. Design principles · **Executable domain model**

## Meaning and purpose

OOP groups state and behavior behind clear contracts. Encapsulation protects invariants; abstraction hides details; polymorphism lets implementations satisfy the same interface. Inheritance is one tool, and composition is often simpler.

## How the example works

Line is an immutable value object that validates SKU, quantity, and price. OrderRepository is a structural protocol. SqliteOrders and MemoryOrders provide the same place operation. place_order depends on the protocol instead of a particular database, so the business flow can run with either adapter.

Implementation: [architect_lab/domain.py](../../architect_lab/domain.py), [architect_lab/storage.py](../../architect_lab/storage.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab orders
```

Expected result: The SQLite and memory adapters return total=3000 for the same input. Contract tests verify stable identity on retries and a conflict when the request changes.

## Tradeoffs and failure cases

A class is useful when it protects a coherent state or contract. A class for every function increases navigation cost. The memory adapter deliberately lacks SQLite durability and concurrent-writer guarantees.

## Practice and interview discussion

Add a file-backed adapter and run the shared contract tests. Explain which guarantees belong to the interface and which belong to the implementation. Interview phrase: I depend on a small interface and keep invariants inside the domain.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.python.org/3/library/http.server.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
