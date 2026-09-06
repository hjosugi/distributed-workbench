# 52. Estimation

[All 53 topics](../ROADMAP.md) · 8. Supporting skills · **PERT and critical-path calculator**

## Meaning and purpose

Estimation expresses uncertainty about effort, duration, and dependencies. Person-days and calendar days are different. Parallel tasks shorten a schedule only when people, environments, and dependencies allow parallel work.

## How the example works

PERT computes (optimistic + 4*likely + pessimistic)/6. The critical-path function traverses a dependency graph, detects cycles, and adds the longest predecessor duration. The fixture has schema work followed by API and UI work, then a release.

Implementation: [architect_lab/planning.py](../../architect_lab/planning.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab planning
```

Expected result: PERT(2,4,8) is about 4.33 days. The dependency schedule is six days along schema, API, release rather than the sum of every task.

## Tradeoffs and failure cases

This is an unconstrained-resource planning model, not a promise or confidence interval. It omits weekends, capacity limits, interruptions, and correlated risks. A single weighted mean hides tail risk.

## Practice and interview discussion

Add a one-person staffing constraint and explain why the six-day schedule may no longer be feasible. Interview phrase: I estimate a range, model dependencies, and separate effort from duration.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://sre.google/workbook/incident-response/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
