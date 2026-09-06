# 49. Decision Making

[All 53 topics](../ROADMAP.md) · 8. Supporting skills · **ADR with alternatives and revisit criteria**

## Meaning and purpose

Decision making turns incomplete information into an explicit, reviewable choice. Separate facts, assumptions, preferences, and hard constraints. Reversible decisions can often be made quickly; expensive irreversible decisions deserve stronger evidence.

## How the example works

The concrete ADR compares a modular application with independent services. It records the chosen local-first design, consequences, rejected alternatives, and conditions that would justify changing it. The matrix makes the preference calculation visible without pretending it proves the answer.

Implementation: [docs/adr/0001-start-simple.md](../../docs/adr/0001-start-simple.md), [architect_lab/planning.py](../../architect_lab/planning.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab planning
```

Expected result: A reader can identify why the choice was made and what new evidence would change it. The calculation is reproducible from the supplied weights.

## Tradeoffs and failure cases

An ADR should not become a long document that hides the decision. A rejected option may become correct later. Do not rewrite history when changing direction; write a superseding decision and link the old one.

## Practice and interview discussion

Use the template to decide whether analytics needs a separate database. Interview phrase: I document the decision, the alternatives, and the conditions for revisiting it.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://martinfowler.com/bliki/PresentationDomainDataLayering.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
