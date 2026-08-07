# NSQ Reliable Worker

NSQのat-least-once deliveryを前提にした、実用寄りのjob processing sampleです。

## 入っているもの

- `cmd/api`: HTTP Job API + durable JSONL outbox
- `cmd/worker`: NSQ consumer + idempotency + retry + DLQ + metrics
- `internal/nsqmini`: Go標準ライブラリだけで実装したNSQ V2 protocol client
- `migrations/postgres.sql`: file storeをPostgreSQLへ移行するschema

## 起動

リポジトリrootで:

```bash
docker compose up --build nsqlookupd nsqd nsqadmin nsq-api nsq-worker
```

## Job投入

```bash
curl -sS http://localhost:8082/jobs \
  -H 'content-type: application/json' \
  -H 'Idempotency-Key: demo-email-001' \
  -d '{
    "type": "send-email",
    "payload": {"to": "demo@example.com"},
    "fail_until_attempt": 2,
    "work_ms": 250
  }'
```

同じ`Idempotency-Key`を再送すると `409 Conflict` になります。

## 観測

- API: `http://localhost:8082`
- NSQ Admin: `http://localhost:4171`
- Worker health: `http://localhost:8083/healthz`
- Worker metrics: `http://localhost:8083/metrics`

## 意図的な失敗

`fail_until_attempt: 2` はattempt 1と2で`REQ`し、attempt 3で成功します。

`fail_until_attempt`を`MAX_ATTEMPTS`以上にすると、最終的に`jobs_dlq`へ送られます。

## crash consistency

APIはjobをoutboxへfsyncしてから202を返します。publish成功直後、sent記録前にcrashすると同じjobを再publishする可能性があります。これは意図したat-least-once動作で、worker側のprocessed storeが重複したbusiness effectを防ぎます。

## Productionへ進める場合

- JSONL outboxとprocessed storeをPostgreSQL transactionへ置換
- NSQ TLS/Authを有効化
- nsqlookupd discoveryをconsumerへ追加
- DLQ replay APIとretentionを追加
- side effectとprocessed message insertを同じDB transactionへ入れる
