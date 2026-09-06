# 40. DNS

[All 53 topics](../ROADMAP.md) · 7. Networking and security · **Real loopback UDP packet exchange**

## Meaning and purpose

DNS maps names to records such as IPv4 A, IPv6 AAAA, and aliases. Resolvers query a hierarchy and cache results according to TTL. DNS resolution is separate from establishing a TCP or TLS connection.

## How the example works

The lab sends a real DNS-format UDP query for orders.test to an ephemeral loopback server. The response copies the transaction ID, returns an authoritative A record with a 30-second TTL, and uses a compression pointer for the answer name.

Implementation: [architect_lab/networking.py](../../architect_lab/networking.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab.networking
```

Expected result: The reply maps orders.test to 127.0.0.1. The client verifies the response source and transaction ID. No external DNS server is contacted.

## Tradeoffs and failure cases

This is a one-question fixture, not a recursive resolver or a general DNS parser. It does not implement caching, DNSSEC, truncation, TCP fallback, or arbitrary record types. A low TTL alone does not guarantee instant client failover.

## Practice and interview discussion

Explain resolver cache, authoritative server, TTL, and negative caching. Ask what happens when DNS succeeds but the application is down. Interview phrase: Name resolution and service health are different steps.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://www.rfc-editor.org/rfc/rfc1035.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
