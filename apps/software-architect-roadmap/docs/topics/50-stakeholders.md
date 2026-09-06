# 50. Stakeholder Management

[All 53 topics](../ROADMAP.md) · 8. Supporting skills · **Concrete RACI and review plan**

## Meaning and purpose

Stakeholder management identifies who is affected, who decides, who contributes expertise, and who needs updates. Different stakeholders may optimize delivery speed, cost, security, or customer experience.

## How the example works

The RACI example assigns one accountable owner and at least one responsible implementer to a release activity. The validator checks these rules. The accompanying plan gives Product, Engineering, and Operations a specific review question and decision deadline.

Implementation: [docs/WORKING_WITH_PEOPLE.md](../../docs/WORKING_WITH_PEOPLE.md), [architect_lab/planning.py](../../architect_lab/planning.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab planning
```

Expected result: raci_valid is true for the supplied roles. Multiple accountable owners or no responsible owner fail validation.

## Tradeoffs and failure cases

RACI is a communication aid, not an organizational law. The simplified validator uses one role per person/activity and cannot judge real authority or team dynamics. A named owner still needs context and time to make a decision.

## Practice and interview discussion

Prepare a short response when Product wants speed and Operations wants a rollback rehearsal. State the tradeoff and propose a measurable release condition. Interview phrase: I make decision ownership and expectations explicit.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://sre.google/workbook/incident-response/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
