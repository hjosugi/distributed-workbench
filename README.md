# Distributed Workbench

Harbor、NSQ、ブラウザ内PostgreSQLを、別々の断片ではなく1つのモノレポにまとめた実用サンプル集です。

## まず見る場所

| ディレクトリ | 何ができるか | 主な独自性 |
|---|---|---|
| `apps/harbor-observer` | 複数HarborサーバのHTTP応答を同時に検査 | 同一パスのSHA-256比較、divergence判定、履歴保存 |
| `apps/nsq-reliable-worker` | NSQでジョブ投入・再試行・重複排除・DLQ | 外部client libraryなしのNSQ V2 consumer、durable outbox、idempotent worker |
| `apps/pgplay-recipes` | PGliteでPostgreSQLをブラウザ内実行 | Harbor/NSQ向けschema recipe、EXPLAIN、URL共有、IndexedDB永続化 |

詳しい役割分担は [`docs/PROJECTS.md`](docs/PROJECTS.md)、採用理由と調査元は [`docs/REFERENCES.md`](docs/REFERENCES.md)、GitHub公開手順は [`docs/PUBLISH.md`](docs/PUBLISH.md) を参照してください。

## 最短の起動方法

### 全部Dockerで起動

```bash
docker compose up --build
```

起動後:

- Harbor Observer: `http://localhost:8081`
- NSQ Job API: `http://localhost:8082`
- NSQ Worker metrics: `http://localhost:8083/metrics`
- NSQ Admin: `http://localhost:4171`
- PostgreSQL Workbench: `http://localhost:5173`

Harbor Observerは、初期設定ではホストPCの `http://localhost:3000` を調べます。外部サーバを使う場合は `HARBOR_SERVERS` を変更してください。

### Go部分だけテスト

```bash
make test
```

### NSQの動作確認

```bash
curl -sS http://localhost:8082/jobs \
  -H 'content-type: application/json' \
  -d '{
    "type": "send-email",
    "payload": {"to": "demo@example.com"},
    "fail_until_attempt": 2
  }'
```

`fail_until_attempt: 2` により、最初の2回は意図的に失敗し、その後成功します。NSQ Adminとworker metricsで再試行を確認できます。

## リポジトリ構成

```text
distributed-workbench/
├── apps/
│   ├── harbor-observer/
│   ├── nsq-reliable-worker/
│   └── pgplay-recipes/
├── docs/
├── compose.yaml
├── go.work
└── Makefile
```

## 方針

このリポジトリは「ライブラリを呼んだだけのhello world」ではありません。

- Harbor: 複数サーバを比較し、欠落・改変・障害を観測する
- NSQ: at-least-once deliveryを前提に、重複排除・retry・DLQを実装する
- PostgreSQL: 上記2つのproduction schemaをブラウザだけで試せる

## 注意

- Harbor本体やPolycentric Protocolのコードは同梱していません。
- Harbor Observerは設定済みサーバに対してのみ相対パスをprobeし、任意URLへのproxyにはなりません。
- NSQ sampleのfile-backed storeは単一instance向けです。複数instanceで運用するときは同梱のPostgreSQL migrationへ置き換えてください。
- `apps/pgplay-recipes` はPGlite `0.5.4` を使用します。
