# 48. Technology evaluation

[All 53 topics](../ROADMAP.md) · 8. Supporting skills · **Decision matrix and evaluation record**

## Meaning and purpose

Technology evaluation compares options against explicit requirements. Popularity alone does not establish fit. A decision should capture current evidence, uncertainty, reversibility, and a reason to revisit the choice.

## How the example works

The weighted matrix scores simplicity and scaling potential from 1 to 5. With simplicity weighted three times as much as scale, a modular monolith ranks above microservices. The ADR records the small-team learning context and the trigger for reconsidering the boundary.

Implementation: [architect_lab/planning.py](../../architect_lab/planning.py), [docs/adr/0001-start-simple.md](../../docs/adr/0001-start-simple.md).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab planning
```

Expected result: The demo ranks modular-monolith first. A test reverses the dominant weight and demonstrates that a different requirement can change the decision.

## Tradeoffs and failure cases

Scores are judgments, not measurements. Weights can hide bias and false precision. A hard requirement such as data residency or required latency should reject an option before weighted scoring.

## Practice and interview discussion

Add operational cost and evaluate sensitivity to the weights. Identify one uncertain assumption worth a short proof of concept. Interview phrase: I compare options against requirements and record the assumptions.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://sre.google/sre-book/monitoring-distributed-systems/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
