# 16. MVC pattern

[All 53 topics](../ROADMAP.md) · 3. Design principles · **HTTP controller and HTML view**

## Meaning and purpose

MVC separates model, view, and controller responsibilities. The controller handles user actions, the model owns data and behavior, and the view renders the result. MVC is primarily a presentation organization pattern, not a complete distributed architecture.

## How the example works

POST /orders is the controller boundary. It validates JSON and delegates to the use case. The domain and repository provide the model. GET / renders an HTML table from stored orders and escapes the ID before inserting it into HTML. The rendering is deliberately small so all three responsibilities remain visible.

Implementation: [architect_lab/server.py](../../architect_lab/server.py), [architect_lab/domain.py](../../architect_lab/domain.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab.server
```

Expected result: After submitting data/order.json, opening localhost:8080 shows the order ID and total. GET /orders exposes the same state as JSON.

## Tradeoffs and failure cases

A large real view should move into a template module. Do not put SQL, payment decisions, or authorization policy into templates. JSON APIs may have no HTML view but still benefit from separating transport and domain logic.

## Practice and interview discussion

Add an HTML order count without changing pricing rules or storage behavior. Explain MVC versus layered architecture: they separate responsibilities at different scopes. Interview phrase: The controller translates input, and the model owns the business rule.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://martinfowler.com/bliki/PresentationDomainDataLayering.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
