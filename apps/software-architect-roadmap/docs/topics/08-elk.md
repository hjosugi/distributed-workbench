# 08. ELK: Elasticsearch, Logstash, Kibana

[All 53 topics](../ROADMAP.md) · 2. Tools · **Real integration configuration**

## Meaning and purpose

ELK is a log ingestion, search, and visualization stack. Logstash accepts and transforms events, Elasticsearch indexes them, and Kibana helps query them. Structured fields make it possible to investigate a request across components.

## How the example works

The sample sends newline-delimited JSON over TCP to Logstash. Its json_lines codec separates events. An output writes daily architect-logs indices. Each event carries service, status, request_id, and duration_ms. Kibana can create a data view over architect-logs-* and filter status=409.

Implementation: [infra/elk/compose.yaml](../../infra/elk/compose.yaml), [infra/elk/pipeline.conf](../../infra/elk/pipeline.conf), [scripts/send_logs.py](../../scripts/send_logs.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
docker compose -f infra/elk/compose.yaml up -d
```

Expected result: After services are ready, python3 scripts/send_logs.py sends three events. Search for them in Kibana at localhost:5601. See the integration guide for the exact Elasticsearch query.

## Tradeoffs and failure cases

The local profile disables Elasticsearch authentication and binds host ports to loopback; it is not a deployable production configuration. Logs may arrive late, indexing may fail, and retention can grow storage costs. Never log bearer tokens or passwords.

## Practice and interview discussion

Find the conflict event, group errors by service, and define a retention period. Distinguish logs, metrics, and traces. Interview phrase: I use structured logs with request identifiers to investigate failures.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://www.elastic.co/docs/reference/logstash/plugins/plugins-codecs-json_lines). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
