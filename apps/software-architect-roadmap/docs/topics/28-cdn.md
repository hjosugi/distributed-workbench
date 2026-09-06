# 28. CDN

[All 53 topics](../ROADMAP.md) · 5. Platform knowledge · **Local reverse-proxy cache simulation**

## Meaning and purpose

A CDN places cached content near clients and can reduce origin traffic. Cache keys, TTLs, invalidation, and private data rules determine correctness. A local proxy can teach cache behavior but does not model a geographically distributed CDN.

## How the example works

NGINX caches only the public product endpoint for 30 seconds and exposes X-Cache. A cache lock reduces simultaneous origin fills. Authorization-bearing requests bypass cache reads and writes. Orders remain uncached.

Implementation: [infra/nginx.conf](../../infra/nginx.conf), [compose.yaml](../../compose.yaml).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
docker compose up --build -d
```

Expected result: Repeated requests to localhost:8088/products show MISS followed by HIT. After expiry, the proxy fetches a fresh response.

## Tradeoffs and failure cases

This is a local edge-cache model, not a CDN deployment. Cache keys must include all inputs that affect representation. TTLs trade staleness for lower latency and origin load; personalized content must not enter a shared public cache.

## Practice and interview discussion

Change a catalog price and observe the stale interval. Decide whether a quote endpoint may reuse the cache. Interview phrase: I cache public reads and make freshness requirements explicit.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://nginx.org/en/docs/http/ngx_http_proxy_module.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
