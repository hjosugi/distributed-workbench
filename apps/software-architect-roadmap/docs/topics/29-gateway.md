# 29. API Gateway

[All 53 topics](../ROADMAP.md) · 5. Platform knowledge · **NGINX routing and rate-limit configuration**

## Meaning and purpose

An API gateway centralizes entry-point concerns such as routing, quotas, authentication enforcement, and request observability. Business invariants should remain with the owning service.

## How the example works

The real NGINX configuration routes product reads to Catalog and other requests to Orders. It bounds upstream connection/read waits and applies a request-rate limit with 429 responses. Separately, the Python TokenBucket model shows burst capacity and refill with a controlled clock.

Implementation: [infra/nginx.conf](../../infra/nginx.conf), [architect_lab/distributed.py](../../architect_lab/distributed.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab distributed
```

Expected result: The model admits requests at times [0,0,0,1] as [true,true,false,true]. In Docker, send a burst to the gateway and observe 429 after the configured burst is exhausted.

## Tradeoffs and failure cases

NGINX limit_req uses its own rate-limiting algorithm; it is not the Python token-bucket implementation. IP-based quotas may unfairly group users behind NAT. Production quotas normally use trusted identity and shared state across gateway replicas.

## Practice and interview discussion

Explain the difference between local and global quotas and when a gateway should return 429 versus 503. Interview phrase: I limit load at the boundary and keep business rules in the service.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://nginx.org/en/docs/http/ngx_http_proxy_module.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
