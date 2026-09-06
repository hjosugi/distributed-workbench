# 07. Jira

[All 53 topics](../ROADMAP.md) · 2. Tools · **Concrete issue payload and workflow exercise**

## Meaning and purpose

Jira tracks work, acceptance criteria, ownership, and dependencies. It does not replace architecture reasoning. A useful task describes a user-visible result and how to verify it, not only an implementation activity.

## How the example works

The sample uses Jira Cloud REST v3 fields and Atlassian Document Format for the description. It describes idempotent order creation, conflicting request keys, and atomic rollback. LAB is a placeholder project key; issue types and required fields depend on the target Jira project. The JSON is an export artifact, not an automatic remote write.

Implementation: [data/jira-issue.json](../../data/jira-issue.json), [docs/WORKING_WITH_PEOPLE.md](../../docs/WORKING_WITH_PEOPLE.md).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m json.tool data/jira-issue.json
```

Expected result: A valid JSON object with project, summary, issue type, and testable acceptance criteria. An existing authorized Jira integration can submit it after adapting project metadata.

## Tradeoffs and failure cases

Valid JSON alone does not guarantee the Jira API accepts it. Required custom fields, project permissions, and issue type names vary. No external Jira issues or messages are created by the exercise.

## Practice and interview discussion

Split the issue into API, persistence, and failure-test tasks. Preserve the end-to-end acceptance criteria. Interview phrase: I define done as observable behavior, not just completed code.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
