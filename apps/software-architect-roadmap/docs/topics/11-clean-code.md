# 11. Clean Code

[All 53 topics](../ROADMAP.md) · 3. Design principles · **Executable functional core and adapters**

## Meaning and purpose

Clean code reduces the effort needed to understand and change behavior. Clear names, small cohesive operations, explicit inputs, and visible side effects matter more than a fixed line-count rule.

## How the example works

The pure total function handles pricing arithmetic. HTTP parsing stays in server.py, database transactions stay in storage.py, and time/network effects are explicit in other modules. Integer money avoids floating-point rounding. Error messages name the rejected condition instead of returning an unexplained failure.

Implementation: [architect_lab/domain.py](../../architect_lab/domain.py), [architect_lab/server.py](../../architect_lab/server.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m unittest discover -s tests -p test_core.py -v
```

Expected result: Domain tests run without HTTP. Invalid quantities fail before persistence, and the HTTP tests independently check translation into 400 and 409 responses.

## Tradeoffs and failure cases

Over-abstraction can hide a simple rule behind many files. Duplicated boundary validation can be intentional, but business rules should have one authoritative owner. Tests should protect behavior rather than private function calls.

## Practice and interview discussion

Implement a maximum order size in the pure core, then show how HTTP and a future CLI both receive the rule. Interview phrase: I keep side effects at the boundary and business rules easy to test.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://martinfowler.com/bliki/TestDrivenDevelopment.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
