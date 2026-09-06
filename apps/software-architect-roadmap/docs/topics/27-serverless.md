# 27. Serverless

[All 53 topics](../ROADMAP.md) · 5. Platform knowledge · **Lambda handler and SAM template**

## Meaning and purpose

Serverless shifts server provisioning and scaling to the platform. Functions usually have bounded execution time and ephemeral local storage. Invocation, retries, concurrency limits, and cold starts remain part of the design.

## How the example works

The Lambda handler validates quantities and returns a stateless quote as an HTTP-style response. SAM points to the same handler, so local invocation and a future AWS deployment share code. The pure quote has no order-creation side effect and needs no idempotency store.

Implementation: [examples/serverless/handler.py](../../examples/serverless/handler.py), [infra/cloud/sam.yaml](../../infra/cloud/sam.yaml), [data/lambda-event.json](../../data/lambda-event.json).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 examples/serverless/handler.py
```

Expected result: Quantities [2,1] return total=3600. Invalid quantities return statusCode=400. sam local invoke exercises the Lambda container when SAM CLI and Docker are available.

## Tradeoffs and failure cases

Running the Python function is not evidence of a successful Lambda deployment. A state-changing function would need a durable idempotency mechanism and explicit event-source retry semantics.

## Practice and interview discussion

Explain where you would store a payment deduplication key and why /tmp is unsuitable. Interview phrase: I keep the function stateless and put durable state in an external store.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/using-sam-cli-local-invoke.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
