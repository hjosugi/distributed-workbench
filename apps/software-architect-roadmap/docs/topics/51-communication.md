# 51. Communication

[All 53 topics](../ROADMAP.md) · 8. Supporting skills · **Architecture brief and incident update examples**

## Meaning and purpose

Good technical communication makes the audience able to decide or act. Start with the result or request, then provide the evidence and uncertainty needed to assess it. The right detail depends on the audience.

## How the example works

The working-with-people guide contains a decision brief, a change notice, and an incident update using the order-system scenario. Each names customer impact, known facts, current action, and the next update. The system-design script explains the same architecture in plain interview English.

Implementation: [docs/WORKING_WITH_PEOPLE.md](../../docs/WORKING_WITH_PEOPLE.md), [docs/SYSTEM_DESIGN.md](../../docs/SYSTEM_DESIGN.md).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 scripts/check_docs.py
```

Expected result: A reader can answer what changed, why it matters, what remains uncertain, and what happens next. These are worked examples, not messages sent to real people.

## Tradeoffs and failure cases

Jargon can hide missing reasoning. Too much low-level detail may obscure the decision. Do not present a hypothesis as an established cause or promise a recovery time without evidence.

## Practice and interview discussion

Explain the outbox to a product manager in three sentences, then to an engineer with the failure window included. Interview phrase: I lead with impact, state what we know, and explain the next action.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://sre.google/workbook/incident-response/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
