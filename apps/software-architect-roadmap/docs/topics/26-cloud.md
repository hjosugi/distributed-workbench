# 26. Cloud

[All 53 topics](../ROADMAP.md) · 5. Platform knowledge · **AWS CloudFormation template**

## Meaning and purpose

Cloud platforms offer managed compute, storage, networking, and identity capabilities. Architecture decisions still require reliability, security, location, cost, and recovery requirements. Managed does not mean operationally invisible.

## How the example works

The CloudFormation template declares a private S3 bucket with versioning and server-side encryption. Public access is blocked. Retain policies avoid accidental object deletion when the stack is removed. Physical bucket naming is left to CloudFormation to avoid a global-name collision.

Implementation: [infra/cloud/storage.yaml](../../infra/cloud/storage.yaml).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 scripts/check_configs.py
```

Expected result: The local checker parses the template. If deliberately deployed in an AWS account, CloudFormation returns the created bucket name. No cloud resources are deployed by the normal lab commands.

## Tradeoffs and failure cases

Retained resources can keep generating cost. This template is not a complete IAM policy, backup strategy, or disaster-recovery plan. Region choice and residency requirements must be explicit before deployment.

## Practice and interview discussion

Define RPO, RTO, allowed regions, retention, and who can read exports. Interview phrase: I choose managed services based on the operational requirements and failure model.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-s3-bucket.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
