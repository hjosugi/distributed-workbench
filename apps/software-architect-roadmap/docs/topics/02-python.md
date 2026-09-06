# 02. Python

[All 53 topics](../ROADMAP.md) · 1. Programming languages · **Executable HTTP service and core labs**

## Meaning and purpose

Python supports fast iteration and readable business rules. Type hints describe contracts but do not validate untrusted input at runtime. The core labs use the standard library so the mechanisms are visible and easy to run.

## How the example works

The catalog uses ThreadingHTTPServer for independent requests. The order core uses frozen dataclasses for line items and explicit validation. An HTTP adapter translates JSON into domain values before calling the repository port. Tests call the same domain functions without starting a server.

Implementation: [examples/catalog/python/catalog.py](../../examples/catalog/python/catalog.py), [architect_lab/domain.py](../../architect_lab/domain.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 examples/catalog/python/catalog.py
```

Expected result: The catalog has the same products and status codes as Java, Go, and JavaScript. In another terminal, python3 scripts/check_catalogs.py python starts and checks an isolated instance.

## Tradeoffs and failure cases

Python http.server is for this local exercise, not a production serving stack. CPU-heavy work may need processes or native code; behavior depends on the Python runtime and build. Thread safety still matters for shared mutable state.

## Practice and interview discussion

Give quantity=true, quantity=0, and an unknown product to the order API. Explain why bool needs special handling when checking integer inputs in Python. Interview phrase: I validate input at the boundary and keep the core simple.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.python.org/3/library/http.server.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
