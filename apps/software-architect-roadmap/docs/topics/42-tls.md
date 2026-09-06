# 42. TLS

[All 53 topics](../ROADMAP.md) · 7. Networking and security · **Real certificate-verified TLS handshake**

## Meaning and purpose

TLS protects transport confidentiality and integrity and authenticates the peer through certificates or other configured mechanisms. A certificate chain is useful only when the client also verifies the intended hostname.

## How the example works

The lab creates a temporary self-signed certificate with localhost and 127.0.0.1 subject alternative names. The server uses SSLContext and permits TLS 1.2 or later. The client explicitly trusts only that lab certificate and performs normal hostname validation.

Implementation: [architect_lab/networking.py](../../architect_lab/networking.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab.networking
```

Expected result: A trusted connection succeeds. A connection using wrong.test as the expected hostname fails with certificate verification error. Temporary key files are removed afterward.

## Tradeoffs and failure cases

This is a local certificate fixture, not a public certificate authority or a certificate-renewal service. TLS termination at a proxy creates a separate trust decision for the proxy-to-service connection. Do not disable certificate validation to fix a hostname mismatch.

## Practice and interview discussion

Explain certificate trust, hostname verification, key exchange, and symmetric record encryption. Interview phrase: Encryption is not enough; I also verify the server identity.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://www.rfc-editor.org/rfc/rfc8446.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
