# 47. Credentials

[All 53 topics](../ROADMAP.md) · 7. Networking and security · **Salted password verification and secret handling**

## Meaning and purpose

Credentials prove an identity or grant access: passwords, private keys, API tokens, and session secrets have different lifecycles. Passwords should be verified with a slow salted password hash rather than recoverable encryption.

## How the example works

The example generates a random salt and derives a password hash with scrypt. Verification repeats the derivation and uses constant-time comparison. Two records for the same password differ because their salts differ. Local environment files, certificates, and databases are excluded from Git.

Implementation: [architect_lab/security.py](../../architect_lab/security.py), [.gitignore](../../.gitignore), [requirements-security.txt](../../requirements-security.txt).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab security
```

Expected result: The correct password passes and a wrong password fails. Tests verify unique records for identical passwords. No real user credentials appear in fixtures.

## Tradeoffs and failure cases

The scrypt parameters are modest for a fast educational test and are not a production security recommendation. Benchmark and select current password-storage parameters for your deployment. A salt is public; an API token or signing key is secret. Never put secrets in logs or Git history.

## Practice and interview discussion

Describe credential rotation and emergency revocation. Explain why adding .env to .gitignore does not erase a secret already committed. Interview phrase: I use salted password hashing and keep operational secrets outside source control.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.python.org/3/library/hashlib.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
