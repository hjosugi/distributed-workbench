# 43. HTTPS

[All 53 topics](../ROADMAP.md) · 7. Networking and security · **Real HTTP over TLS**

## Meaning and purpose

HTTPS carries HTTP semantics over an authenticated encrypted transport. For HTTP/1.1 and HTTP/2 this commonly uses TLS over TCP; HTTP/3 uses QUIC over UDP with TLS integrated into QUIC. HTTP status and authorization rules still apply.

## How the example works

The same order HTTP server is wrapped in a TLS context. The client sends GET /health over HTTPS using an explicit trusted certificate and receives the usual JSON response. This separates the HTTP application contract from transport setup.

Implementation: [architect_lab/networking.py](../../architect_lab/networking.py), [architect_lab/server.py](../../architect_lab/server.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab.networking
```

Expected result: The result includes https.status=ok and wrong_hostname_rejected=true. The lab negotiates the runtime-supported TLS version above the configured minimum.

## Tradeoffs and failure cases

HTTPS does not hide all metadata, prevent every application vulnerability, or automatically authorize the caller. Mixed-content policy, secure cookies, HSTS, and proxy headers belong to a real browser deployment and are outside this loopback exercise.

## Practice and interview discussion

Draw where TLS terminates in a gateway deployment and decide whether the next hop also needs TLS or mTLS. Interview phrase: HTTPS protects the connection, while the application still checks permissions.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.python.org/3/library/ssl.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
