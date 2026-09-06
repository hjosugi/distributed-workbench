# 38. Object Storage

[All 53 topics](../ROADMAP.md) · 6. Data and analytics · **Immutable local objects and S3 template**

## Meaning and purpose

Object storage addresses opaque byte objects by keys and metadata. It is useful for exports, images, archives, and data-lake files. It does not provide the same operations or consistency scope as a relational table or POSIX filesystem.

## How the example works

The local adapter computes a SHA-256 key, writes a temporary file, flushes it, and atomically replaces the destination. Reads validate the key and checksum. The cloud template provides a versioned private S3 bucket for an external implementation.

Implementation: [architect_lab/data.py](../../architect_lab/data.py), [infra/cloud/storage.yaml](../../infra/cloud/storage.yaml).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab data
```

Expected result: Writing identical bytes returns the same key. Corrupting an object causes a checksum error, and path-traversal keys are rejected.

## Tradeoffs and failure cases

The local adapter is not an S3-compatible server and does not claim crash-proof directory metadata durability. The document index is separately process-local. Object lifecycle, access control, metadata, and retention are separate concerns.

## Practice and interview discussion

Design export naming, version retention, and a manifest that references complete objects only. Interview phrase: I store large immutable data as objects and keep queryable metadata separately.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-s3-bucket.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
