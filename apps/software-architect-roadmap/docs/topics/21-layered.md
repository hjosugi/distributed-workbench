# 21. Layered architecture

[All 53 topics](../ROADMAP.md) · 4. Architectural patterns · **Presentation, domain, and persistence separation**

## Meaning and purpose

Layered architecture groups responsibilities such as presentation, application logic, domain rules, and persistence. A layer is a code organization concept; it does not require a separate machine or network hop.

## How the example works

The HTTP handler translates requests, place_order coordinates the use case, total validates pricing rules, and a repository adapter performs SQL. The runtime path crosses these responsibilities, while the domain code has no import of the HTTP server or SQLite implementation.

Implementation: [architect_lab/server.py](../../architect_lab/server.py), [architect_lab/domain.py](../../architect_lab/domain.py), [architect_lab/storage.py](../../architect_lab/storage.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab orders
```

Expected result: The same domain flow runs from the CLI and HTTP adapter. A domain-only test does not need the service process.

## Tradeoffs and failure cases

Layers can become pass-through wrappers with no value. Allowing controllers to execute arbitrary SQL bypasses the boundary. Layering alone does not specify consistency, scaling, or team ownership.

## Practice and interview discussion

Identify which layer should reject a negative quantity and which should translate that rejection to HTTP 400. Interview phrase: I separate responsibilities so a transport change does not change business rules.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://martinfowler.com/bliki/PresentationDomainDataLayering.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
