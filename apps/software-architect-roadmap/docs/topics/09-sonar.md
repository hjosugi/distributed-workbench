# 09. Sonar / SonarQube

[All 53 topics](../ROADMAP.md) · 2. Tools · **Scanner configuration**

## Meaning and purpose

SonarQube performs static analysis and can enforce a quality gate. Static analysis can find suspicious code without executing each path. It complements behavior tests, code review, and security analysis.

## How the example works

The scanner properties name a project, identify production and test roots, set UTF-8 and the Python version, and exclude test files nested under examples. Start a compatible SonarQube service, configure SONAR_HOST_URL and SONAR_TOKEN locally, and invoke sonar-scanner from this module. The token is never placed in the properties file.

Implementation: [sonar-project.properties](../../sonar-project.properties).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m compileall -q architect_lab examples
```

Expected result: The local command checks syntax only. A Sonar scan produces findings and a quality-gate result after a real server and scanner are configured. The repository does not claim a completed scan.

## Tradeoffs and failure cases

False positives and missing findings are both possible. A green gate does not prove correctness or security. Scanner/server compatibility and available analyzers depend on the selected SonarQube edition and version.

## Practice and interview discussion

Review a finding about duplicated validation and decide whether the duplication protects a boundary or indicates accidental design drift. Interview phrase: Static analysis is one signal, and I verify important behavior with tests.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/scanners/sonarscanner). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
