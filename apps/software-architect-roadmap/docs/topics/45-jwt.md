# 45. JWT

[All 53 topics](../ROADMAP.md) · 7. Networking and security · **Fixed-algorithm educational signer and verifier**

## Meaning and purpose

A JWT is a claims format. A signed JWT normally provides integrity, not confidentiality; its header and payload can be decoded. A token is accepted only after signature and application-specific claim checks.

## How the example works

The lab supports only HS256 with a sufficiently long random key and an exact expected header. It verifies the signature with a constant-time comparison, then checks expiry, issuer, audience, subject, and optional activation/issue time. Tests reject algorithm substitution and modified claims.

Implementation: [architect_lab/security.py](../../architect_lab/security.py), [tests/test_security.py](../../tests/test_security.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab security
```

Expected result: A valid token returns the demo subject. Tampering, expiry at the boundary, a wrong issuer, a wrong audience, and future activation all fail.

## Tradeoffs and failure cases

This small verifier is not a production JWT library. It intentionally excludes JWK discovery, key rotation, asymmetric algorithms, nested tokens, multiple audiences, and revocation. A production system should use a maintained JOSE library and a documented validation policy.

## Practice and interview discussion

Explain how short expiry and revocation interact. Distinguish an access token from an ID token. Interview phrase: I verify the algorithm, signature, issuer, audience, and expiry before trusting claims.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://www.rfc-editor.org/rfc/rfc8725.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
