# 53. Leadership

[All 53 topics](../ROADMAP.md) · 8. Supporting skills · **Incident exercise and ownership practices**

## Meaning and purpose

Technical leadership helps a team make sound decisions and deliver reliable outcomes. It includes creating clarity, sharing context, developing others, and accepting responsibility for tradeoffs. It does not require making every technical choice personally.

## How the example works

The incident exercise assigns a coordinator, an investigator, and a communicator after duplicate charges are reported. The team first limits impact, keeps a factual timeline, verifies recovery, and records follow-up actions with owners. A separate review exercise asks a junior engineer to explain an invariant before proposing code.

Implementation: [docs/WORKING_WITH_PEOPLE.md](../../docs/WORKING_WITH_PEOPLE.md), [docs/EXERCISES.md](../../docs/EXERCISES.md).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 scripts/check_docs.py
```

Expected result: The artifact contains a concrete incident timeline, ownership table, and review checklist. No real incident is declared and no messages are sent.

## Tradeoffs and failure cases

A coordinator who also performs every investigation can become a bottleneck. Blame discourages early reporting. A retrospective without owned, verifiable follow-ups rarely changes future behavior.

## Practice and interview discussion

Run a 15-minute tabletop exercise: the broker is healthy but the revenue projection stops advancing. Decide who coordinates, who investigates, and what you tell stakeholders. Interview phrase: I create clarity, delegate investigation, and keep the team focused on recovery.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://sre.google/workbook/incident-response/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
