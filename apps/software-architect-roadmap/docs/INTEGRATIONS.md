# 外部サービスと4言語の起動手順

すべて `apps/software-architect-roadmap` から実行します。各コマンドは教材専用のローカル環境を想定しています。実際に確認した範囲は [VALIDATION.md](VALIDATION.md) を参照してください。

## 4言語のCatalog API

各サービスは同じポート8081を使うため、単体起動は1つずつ行います。共通検証スクリプトは空いているポートを選択し、正常系・404・405を確認してプロセスを終了します。

| 言語 | 必要環境 | 起動 |
|---|---|---|
| Java | JDK 17以上 | `java examples/catalog/java/Catalog.java` |
| Python | Python 3.12以上 | `python3 examples/catalog/python/catalog.py` |
| Go | Go 1.24以上 | `GOWORK=off go run examples/catalog/go/main.go` |
| JavaScript | Node.js 24 | `node examples/catalog/javascript/catalog.mjs` |

```bash
python3 scripts/check_catalogs.py python javascript java go
node --test examples/catalog/javascript/catalog.test.mjs
(cd examples/catalog/go && GOWORK=off go test ./...)
```

4言語のうち導入済みのものだけ確認する場合、引数から未導入の言語を外します。Javaのsource-file launchにはJDKのcompiler moduleが必要です。

Dockerなしで別プロセスの連携を見る場合、Node Catalogを起動した別ターミナルで:

```bash
CATALOG_URL=http://127.0.0.1:8081 python3 -m architect_lab.server
```

## Docker、Gateway、cache

```bash
docker compose config --quiet
docker compose up --build --wait
python3 scripts/smoke_http.py
curl -i http://127.0.0.1:8088/products
curl -i http://127.0.0.1:8088/products
```

`X-Cache` がMISSからHITに変わります。注文APIはキャッシュされません。GatewayはIP単位で5リクエスト/秒、burst 10の制限を持ち、超過時に429を返します。これはNGINXの `limit_req` であり、Pythonのtoken bucketと同じ実装ではありません。

```bash
docker compose logs --tail 30 orders catalog gateway
docker compose down
```

## KafkaとRedis

```bash
docker compose --profile data up -d kafka redis
docker compose ps
```

Kafkaがhealthyになってから:

```bash
python3 scripts/kafka_roundtrip.py
```

このスクリプトは固有名のtopicを作り、3件のJSONイベントをpublishし、2つのconsumer groupで同じデータを確認し、自分が作ったtopicだけを削除します。ローカルoutbox dispatcherとの結合は行っていません。

Redisの実操作:

```bash
docker compose exec -T redis redis-cli HSET architect:product:book name Book price 1200
docker compose exec -T redis redis-cli HGETALL architect:product:book
docker compose exec -T redis redis-cli EXPIRE architect:product:book 60
docker compose exec -T redis redis-cli TTL architect:product:book
```

Redisはappend-only persistenceとvolume付きです。Kafkaは単一broker・replication factor 1・永続volumeなしの使い捨てラボです。hostにKafka/Redisのポートは公開せず、操作はコンテナ内部から行います。

```bash
docker compose --profile data down
```

Kafka設定は [公式Quickstart](https://kafka.apache.org/quickstart/) を基にしています。教材のimageは `apache/kafka:4.3.1`。Redis等のminor tagは更新されるため、厳密な再現には動作確認後にdigestを固定してください。

## ELK

メモリに余裕のあるDocker環境で実行します。

```bash
docker compose -f infra/elk/compose.yaml config --quiet
docker compose -f infra/elk/compose.yaml up -d
docker compose -f infra/elk/compose.yaml logs --tail 30 logstash
```

LogstashがTCP 5000で待ち受け、Elasticsearchが応答する状態になったら:

```bash
python3 scripts/send_logs.py
curl -fsS 'http://127.0.0.1:9200/architect-logs-*/_search?pretty'
```

Kibanaは `http://127.0.0.1:5601`。Data Viewで `architect-logs-*` を指定し、Discoverで `status:409` を検索します。起動直後はindex作成やrefreshを待ってください。

```bash
docker compose -f infra/elk/compose.yaml down
```

3製品を8.19.0で揃えたローカル設定です。認証を無効化しloopbackに限定しています。本番設定や最新版の推奨ではありません。アップグレード時は3製品の互換性を確認してください。

## Kubernetes / kind

Docker、kind、kubectlが必要です。既存の本番contextではなく、この教材用clusterを使います。

```bash
kind create cluster --name architect-lab
docker build -t architect-orders:local .
kind load docker-image architect-orders:local --name architect-lab
kubectl --context kind-architect-lab apply -f infra/k8s/orders.yaml
kubectl --context kind-architect-lab -n architect-lab rollout status deployment/orders --timeout=120s
kubectl --context kind-architect-lab -n architect-lab port-forward service/orders 8090:80
```

別ターミナル:

```bash
python3 scripts/smoke_http.py http://127.0.0.1:8090
```

このmanifestは内蔵catalog・1 replica・emptyDirです。Pod削除でデータが消えます。複数replica化する前に永続DB設計を変える必要があります。

教材clusterが不要になったら:

```bash
kind delete cluster --name architect-lab
```

参照: [kind公式Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/)。

## Lambda / SAM / CloudFormation

ハンドラー単体:

```bash
python3 examples/serverless/handler.py
```

AWS SAM CLIとDockerがある場合:

```bash
sam validate --template-file infra/cloud/sam.yaml
sam local invoke QuoteFunction --template-file infra/cloud/sam.yaml --event data/lambda-event.json
```

S3のCloudFormationは [storage.yaml](../infra/cloud/storage.yaml) です。private bucket、versioning、encryption、Retainを設定しています。AWSへのdeployはこの教材では実行しません。`Retain` したbucketはstack削除後も残るため、実際に使う場合は保存期間と削除担当を決めてください。

## Hadoop Streaming

ローカル実行:

```bash
python3 examples/hadoop/mapper.py < data/events.jsonl | sort | python3 examples/hadoop/reducer.py
```

Hadoop導入済み環境では、実在するstreaming jarのパスを設定して実行します。全workerにPython 3が必要です。

```bash
export ARCHITECT_STREAMING_JAR=/path/to/installed/hadoop-streaming.jar
hdfs dfs -mkdir -p /tmp/architect-input
hdfs dfs -put -f data/events.jsonl /tmp/architect-input/events.jsonl
hadoop jar "$ARCHITECT_STREAMING_JAR" \
  -files examples/hadoop/mapper.py,examples/hadoop/reducer.py \
  -mapper 'python3 mapper.py' \
  -reducer 'python3 reducer.py' \
  -input /tmp/architect-input \
  -output /tmp/architect-output
hdfs dfs -cat '/tmp/architect-output/part-*'
```

output directoryは未作成である必要があります。再実行時は別名を指定してください。この教材はHDFS/YARN自体を起動しません。[公式Streaming仕様](https://hadoop.apache.org/docs/stable/hadoop-streaming/HadoopStreaming.html)。

## Jenkins、Jira、Sonar

JenkinsではPipeline from SCMで親repoをcheckoutし、Script Pathに `apps/software-architect-roadmap/Jenkinsfile` を指定します。agentにPython 3.12+とNode 24が必要です。

Jiraの [payload](../data/jira-issue.json) はJSON出力例です。project keyやissuetypeを実在する設定に合わせてから、認可された経路でREST v3に送ります。通常のラボ実行では起票しません。

SonarQubeとSonarScanner CLIを導入した環境では、tokenをローカルのsecretとして設定し、モジュールディレクトリから `sonar-scanner` を実行します。`SONAR_HOST_URL` と `SONAR_TOKEN` を利用でき、repoのpropertiesにtokenを記載する必要はありません。scanner/server互換性は [公式資料](https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/scanners/sonarscanner) で確認してください。
