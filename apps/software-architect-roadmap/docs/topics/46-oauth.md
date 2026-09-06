# 46. OAuth

[All 53 topics](../ROADMAP.md) · 7. Networking and security · **Authorization Code with PKCE model**

## Meaning and purpose

OAuth delegates authorization to a client without sharing the resource owner password with that client. OAuth alone is not a user authentication protocol; OpenID Connect adds identity semantics. Modern browser and native flows commonly use Authorization Code with PKCE.

## How the example works

The model begins after hypothetical user authentication and consent. It binds a short-lived code to a registered client, an exact redirect URI, a subject, and an S256 challenge. Token exchange checks the verifier and consumes the code only on success. The PKCE hash is tested with the RFC 7636 example vector.

Implementation: [architect_lab/security.py](../../architect_lab/security.py), [tests/test_security.py](../../tests/test_security.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab security
```

Expected result: One valid exchange succeeds. Wrong client, redirect, verifier, expired code, and replay are rejected.

## Tradeoffs and failure cases

This is not a complete authorization server: there is no login UI, consent screen, browser callback, state store, refresh token, or token endpoint. A full browser client must bind the redirect response to its session and handle CSRF and authorization-response injection. Follow the current OAuth security BCP.

## Practice and interview discussion

Explain what PKCE protects if an authorization code is intercepted. Explain why state and PKCE have distinct roles in a real flow. Interview phrase: I bind the code to the client request and require the PKCE verifier.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://www.rfc-editor.org/rfc/rfc9700.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
