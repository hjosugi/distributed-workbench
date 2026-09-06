# 22. Client-Server

[All 53 topics](../ROADMAP.md) · 4. Architectural patterns · **HTTP client and server contract**

## Meaning and purpose

In client-server architecture, clients request a capability and servers expose it through a contract. The boundary makes location and failure visible. The client must handle errors even when the server implementation is correct.

## How the example works

The smoke client sends JSON and an Idempotency-Key. It verifies 201 on creation, 200 on replay, and 409 when the same key is reused with a different body. Timeouts bound waiting. The server computes prices from its catalog instead of trusting client-supplied amounts.

Implementation: [architect_lab/server.py](../../architect_lab/server.py), [scripts/smoke_http.py](../../scripts/smoke_http.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab.server
```

Expected result: In a second terminal, python3 scripts/smoke_http.py prints a passing contract result. data/order.json provides an inspectable fixture.

## Tradeoffs and failure cases

A timeout does not prove a write failed. Retrying without a stable key can create a second order. This local API has no user accounts; a production key must be scoped to an authenticated caller or tenant.

## Practice and interview discussion

Draw the case where the server commits but the response is lost. Explain how the client safely obtains the original order. Interview phrase: A timeout means the outcome may be unknown.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.python.org/3/library/http.server.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
