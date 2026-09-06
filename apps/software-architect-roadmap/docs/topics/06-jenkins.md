# 06. Jenkins

[All 53 topics](../ROADMAP.md) · 2. Tools · **Pipeline configuration**

## Meaning and purpose

Jenkins runs automation on agents. A Jenkinsfile records build and test steps with the code. The controller schedules work; the agent needs the tools and permissions required by those steps.

## How the example works

The Declarative Pipeline uses a bounded timeout, enters the module directory, runs Python behavior tests, executes all labs, and checks the Node catalog. Configure a Pipeline from SCM and set the script path to apps/software-architect-roadmap/Jenkinsfile. The agent needs Python 3.12+ and Node 24.

Implementation: [Jenkinsfile](../../Jenkinsfile).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m unittest discover -s tests -v
```

Expected result: The local equivalent test command passes. On a configured Jenkins instance, a failed command fails the Test stage. No Jenkins server is created or changed by this repository.

## Tradeoffs and failure cases

A pipeline can fail because the agent lacks tools, the checkout differs, or credentials expired. Use managed credentials and avoid printing environment secrets. Shared agents also need workspace isolation.

## Practice and interview discussion

Add a build stage after tests, and explain why deployment should use the exact tested artifact. Interview phrase: I keep the pipeline in version control and make failures visible.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://www.jenkins.io/doc/book/pipeline/syntax/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
