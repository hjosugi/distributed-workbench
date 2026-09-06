# 05. GitHub

[All 53 topics](../ROADMAP.md) · 2. Tools · **Workflow and repository integration**

## Meaning and purpose

GitHub supports version control collaboration, review, and automated checks. A good repository is a reproducible engineering record: source, tests, design decisions, data, and instructions must agree.

## How the example works

The parent workflow added for this module checks Python labs, four catalog contracts, document links, and Docker configuration. The roadmap manifest maps each image label to a real file. The local checker rejects missing topics or broken internal links, preventing a polished index from hiding empty coverage.

Implementation: [scripts/check_docs.py](../../scripts/check_docs.py), [README.md](../../README.md).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 scripts/check_docs.py
```

Expected result: The document checker reports 53 mapped topics. The parent Actions page shows the actual status for each job after publication.

## Tradeoffs and failure cases

A committed workflow is not evidence that CI passed. Branch protection, approvals, and token scopes depend on repository configuration. Do not commit generated credentials, local databases, or secret environment files.

## Practice and interview discussion

Make a small change to a product contract and inspect the failing CI job. Explain the difference between a branch, a commit, a pull request, and an artifact. Interview phrase: Every change should have a clear review and validation path.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.github.com/en/actions/get-started/quickstart). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
