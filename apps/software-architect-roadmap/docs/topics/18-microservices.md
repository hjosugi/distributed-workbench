# 18. Microservices

[All 53 topics](../ROADMAP.md) · 4. Architectural patterns · **Two real HTTP services**

## Meaning and purpose

Microservices separate business capabilities into services that can be deployed and operated independently. The useful boundary includes ownership and data, not only a different process or port.

## How the example works

The orders service calls a separate catalog service over HTTP. Catalog owns current prices. Orders stores an accepted price snapshot locally. A two-second downstream timeout turns catalog failure into 503 for new orders. A previously accepted request can replay from local storage while the catalog is down.

Implementation: [compose.yaml](../../compose.yaml), [architect_lab/server.py](../../architect_lab/server.py), [examples/catalog/javascript/catalog.mjs](../../examples/catalog/javascript/catalog.mjs).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
docker compose up --build -d
```

Expected result: python3 scripts/smoke_http.py checks create, retry, and conflict through port 8080. The HTTP tests also stop the catalog and verify failure behavior.

## Tradeoffs and failure cases

This is a two-service integration lab, not a complete commerce platform. A synchronous dependency reduces availability for new requests. Independent deployments add network, schema, observability, and ownership costs.

## Practice and interview discussion

Explain when you would keep Catalog as a module. Add a stale-price cache only after defining how long a quote remains valid. Interview phrase: I split services when ownership or scaling needs justify the cost.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://martinfowler.com/articles/microservices.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
