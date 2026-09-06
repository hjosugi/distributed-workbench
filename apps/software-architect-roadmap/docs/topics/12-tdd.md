# 12. TDD

[All 53 topics](../ROADMAP.md) · 3. Design principles · **Behavior tests and red/green/refactor exercise**

## Meaning and purpose

Test-driven development repeats red, green, and refactor. First describe missing behavior in a failing test, then implement the smallest correct change, then improve structure while tests remain green. Existing passing tests alone do not prove that this development process was followed.

## How the example works

The walkthrough asks you to add a bulk-order discount in a separate pure function. It provides a failing test, a first working implementation, and a refactoring target. The main repository already contains completed behavior tests for rollback, idempotency, and concurrency; the exercise is separate from the default passing suite.

Implementation: [tests/test_core.py](../../tests/test_core.py), [docs/TDD_WALKTHROUGH.md](../../docs/TDD_WALKTHROUGH.md).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m unittest discover -s tests -p test_core.py -v
```

Expected result: The current suite passes. In your exercise branch, the new behavior test should fail before implementation and pass afterward. Existing tests must continue to pass.

## Tradeoffs and failure cases

Tests that mirror every private operation become brittle during refactoring. TDD does not replace integration tests, exploratory testing, or architecture judgment. Time-based tests should use controlled clocks where possible.

## Practice and interview discussion

Follow the walkthrough and explain why the test observes a price rather than checking how many helper functions were called. Interview phrase: I write a failing behavior test, implement the rule, and refactor safely.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://martinfowler.com/bliki/TestDrivenDevelopment.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
