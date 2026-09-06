# 31. CI/CD

[All 53 topics](../ROADMAP.md) · 5. Platform knowledge · **Automated validation and release exercise**

## Meaning and purpose

Continuous integration validates frequent changes. Continuous delivery keeps a releasable artifact ready; continuous deployment automatically releases changes that pass the required gates. These terms describe different release commitments.

## How the example works

The parent Actions workflow checks the module and builds its Docker service. The Jenkinsfile offers a second test pipeline example. The release exercise records a commit, test results, image identity, migration compatibility, and rollback criteria before deployment.

Implementation: [Jenkinsfile](../../Jenkinsfile), [scripts/check_docs.py](../../scripts/check_docs.py), [Dockerfile](../../Dockerfile).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m unittest discover -s tests -v
```

Expected result: Local tests pass; after pushing, inspect Actions for the actual result. The artifact and commit should identify the code that was tested.

## Tradeoffs and failure cases

No cloud deployment is triggered by this module. Rebuilding a mutable image tag during deployment can produce different bytes from the tested artifact. Rollback may be unsafe after a destructive schema change.

## Practice and interview discussion

Describe a canary release with one measurable success criterion and one rollback threshold. Interview phrase: I deploy the tested artifact and define rollback before release.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.github.com/en/actions/get-started/quickstart). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
