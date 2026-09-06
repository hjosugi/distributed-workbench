# 44. Encryption

[All 53 topics](../ROADMAP.md) · 7. Networking and security · **AES-GCM authenticated encryption**

## Meaning and purpose

Encryption protects confidentiality. Authenticated encryption also detects unauthorized changes to the ciphertext or associated metadata. Hashing and encoding solve different problems and should not be described as encryption.

## How the example works

The example uses the cryptography library AESGCM implementation, a random 256-bit key, and a fresh 96-bit nonce. It binds order:42 as associated data. Decryption with order:43 fails authentication even though the ciphertext is unchanged.

Implementation: [architect_lab/security.py](../../architect_lab/security.py), [requirements-security.txt](../../requirements-security.txt).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -c "from architect_lab.security import encrypt_roundtrip; print(encrypt_roundtrip())"
```

Expected result: The original text is recovered, and tamper_rejected is true. Install the optional pinned dependency before running this lesson.

## Tradeoffs and failure cases

Never reuse a nonce with the same AES-GCM key. Key generation, storage, rotation, and access policy determine system security. The demonstration creates keys in memory and does not implement KMS or durable key recovery.

## Practice and interview discussion

Explain how envelope encryption separates a data key from a key-encryption key. Explain why base64 is reversible encoding, not encryption. Interview phrase: I use a reviewed authenticated-encryption library and manage keys separately.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://cryptography.io/en/latest/hazmat/primitives/aead/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
