# 17. GoF design patterns

[All 53 topics](../ROADMAP.md) · 3. Design principles · **All 23 executable patterns**

## Meaning and purpose

The GoF catalog contains 23 object-oriented design patterns in creational, structural, and behavioral groups. A pattern names a recurring design problem and the roles that solve it. It is not a checklist that every application should implement.

## How the example works

Each named function contains a complete small example with observable output. Factory Method delegates construction; Abstract Factory creates matching families; Bridge varies abstraction and implementation separately; State delegates behavior to a current state; Visitor adds operations across element types. The companion guide explains all 23 and their common confusions.

Implementation: [architect_lab/gof.py](../../architect_lab/gof.py), [docs/GOF.md](../../docs/GOF.md).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab gof
```

Expected result: 23 named results. Tests verify each example, including independent prototype state, shared flyweight data, one proxy origin call, undo behavior, and rejected early shipping.

## Tradeoffs and failure cases

The Singleton example is process-local and intentionally not a concurrent initialization strategy. In Python, modules, functions, iterators, and decorators often express a pattern without a large class hierarchy. The catalog examples are independent lessons, not production utilities.

## Practice and interview discussion

Compare Strategy with State, Adapter with Bridge, and Decorator with Proxy. Explain the intent before drawing a class diagram. Interview phrase: I use a pattern when it solves a concrete source of change.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-9780321700698). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
