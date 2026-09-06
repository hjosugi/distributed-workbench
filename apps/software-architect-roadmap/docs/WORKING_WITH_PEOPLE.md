# Supporting skills: worked examples

These are fictional examples for the order-system lab. They are not messages sent to real people or reports of actual incidents.

## Technology decision brief

Decision needed: should analytics be a separate service now?

Context: one team, modest traffic, strong order-write invariants, analytics may lag by one minute. Proposal: start with an independent consumer module and a clear event contract. Extract it when ownership or resource isolation requires it. Evidence needed: consumer lag under peak load and operational effort for an additional service. Revisit if analytics load disrupts order latency or a separate team owns it.

## Stakeholder review

| Role | Main concern | Review question | Decision timing |
|---|---|---|---|
| Product | Customer impact | Is a one-minute analytics delay acceptable? | Before committing the event contract |
| Engineering | Correctness | Can a retry or replay duplicate an effect? | Before implementation review |
| Operations | Recovery | Can we replay safely after failure? | Before release |
| Security | Identity and data | Which caller owns an order and which fields may be logged? | Before external exposure |

## Concrete RACI

| Activity | Tech lead | Engineer | Product | Operations |
|---|---|---|---|---|
| Event contract | A | R | C | C |
| Release implementation | A | R | I | C |
| Recovery exercise | C | R | I | A |

R=responsible, A=accountable, C=consulted, I=informed. The local validator requires one A and at least one R per activity. Real organizations may combine roles; adapt the convention explicitly.

## Change notice

The order API now returns the original order when a client retries with the same key and body. Reusing a key with different items returns 409. Clients should keep a stable key across retries and create a new key only for a new business request. The rollout checks duplicate-order rate and HTTP conflict rate. The API owner will review results before wider rollout.

## Incident exercise

Fictional report: revenue doubles after a consumer restart.

| Relative time | Action | Owner |
|---|---|---|
| T+0 | Record scope and assign coordinator | Tech lead |
| T+2 | Pause the affected consumer and preserve offset/evidence | Operations |
| T+5 | Compare event IDs, inbox rows, and projection totals | Investigator |
| T+8 | Send customer-impact update with known facts | Communicator |
| T+12 | Rebuild a disposable projection from the log | Engineer |
| T+15 | Verify totals and agree on recovery | Coordinator |

First update: “The revenue report is overcounting some replayed events. Order creation is still working. We paused the affected consumer and are checking event IDs against projection updates. We will provide the next update after validating a clean replay.”

This is a hypothesis until the evidence confirms the missing deduplication. Do not claim duplicate customer charges from a duplicated report alone.

## Leadership and review

Ask the implementer to state the invariant and show one failure test. Give them ownership of the investigation while keeping the decision and escalation path clear. In a retrospective, record the contributing conditions and a concrete prevention item, such as an atomic inbox/projection transaction plus a restart test.

A useful follow-up has an owner, a due date agreed by the team, and evidence of completion. Blame and vague “be more careful” actions do not improve the system.

## Estimation example

Schema takes 2 days. API takes 3 days after schema. UI takes 2 days after schema. Release takes 1 day after both. With enough independent people, the critical path is schema → API → release = 6 days. Total effort is 8 person-days. With one person, the six-day calendar assumption is no longer valid.

For uncertain work, PERT(2,4,8) = 4.33 days. This is a weighted estimate, not a confidence interval. State staffing, dependency, and interruption assumptions before quoting a date.
