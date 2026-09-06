# Software Architect Roadmap — 53項目の解説と実装

ByteByteGoの画像にある **8分野・53項目** を、コード、設定、図解、テスト、演習に対応させた教材です。共通題材は「注文システム」。GoFは23パターンすべてに個別の実装があります。

- [全53項目の目次](docs/ROADMAP.md)
- [System Design面接用の英語回答・構成図](docs/SYSTEM_DESIGN.md)
- [GoF 23パターン解説](docs/GOF.md)
- [外部サービスの起動手順](docs/INTEGRATIONS.md)
- [障害演習・学習順序](docs/EXERCISES.md)
- [実行確認の結果と範囲](docs/VALIDATION.md)
- [公式資料・一次資料](docs/SOURCES.md)

セットアップは日本語、技術解説と面接スクリプトは暗記しやすい英語です。各トピックに意味、実装の動き、コマンド、期待結果、トレードオフ、障害ケース、演習を載せています。

## 最短で動かす

必要環境: Python 3.12以上。基本ラボには追加パッケージが不要です。Linux/macOS/WSLでは次を実行します。

```bash
git clone https://github.com/hjosugi/distributed-workbench.git
cd distributed-workbench/apps/software-architect-roadmap
python3 -m architect_lab all
python3 -m unittest discover -s tests -v
```

Windows PowerShellでは `python3` を `py -3` に置き換えられます。Hadoopのパイプ例はWSLで実行してください。

暗号化の追加実装とYAML検証を含める場合:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 scripts/check_configs.py
```

AES-GCMテストは `cryptography` がない環境では理由付きでskipします。HTTPSテストにはOpenSSL CLIを使います。CIでは依存を入れて実行します。

## 注文APIを動かす

```bash
python3 -m architect_lab.server
```

別ターミナルから:

```bash
python3 scripts/smoke_http.py
curl -i http://127.0.0.1:8080/orders \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: sample-order-1' \
  --data-binary @data/order.json
```

| 操作 | 結果 |
|---|---|
| サンプルを新規登録 | HTTP 201、合計3000円 |
| 同じkey・同じ内容で再送 | HTTP 200、同じ注文IDと元の金額 |
| 同じkey・違う内容で再送 | HTTP 409 |
| 数量0・負数・小数・bool・未知の商品 | HTTP 400 |
| GET `/orders` | 保存済み注文一覧 |
| GET `/` | MVCのHTML表示例 |
| GET `/health` | 起動状態 |

価格はサーバー側で決定します。受理済み注文の再送は価格変更後やCatalog停止中でも元の結果を返します。keyはこの教材全体で一意です。本番では認証ユーザーやtenantの単位に分けます。

## 収録内容

| 分野 | 項目数 | 実装・成果物 |
|---|---:|---|
| Programming languages | 4 | Java・Python・Go・JavaScriptの共通Catalog API |
| Tools | 5 | GitHub Actions、Jenkinsfile、Jira payload、ELK、Sonar設定 |
| Design principles | 8 | OOP、Clean Code、TDD、DDD、CAP、ACID、MVC、GoF |
| Architectural patterns | 6 | Microservices、Pub/Sub、EDA、Layered、Client-Server、Hexagonal |
| Platform knowledge | 8 | Docker、Kubernetes、CloudFormation、Lambda/SAM、Cache、Gateway、分散モデル、CI/CD |
| Data and analytics | 8 | SQL、NoSQL/Redis、Hadoop、Kafka、window集計、OLAP、object storage、migration |
| Networking and security | 8 | DNS、TCP、TLS/HTTPS、AES-GCM、JWT、OAuth/PKCE、password hashing |
| Supporting skills | 6 | 技術選定、ADR、RACI、伝達例、PERT/critical path、リーダーシップ演習 |

## ラボを個別に実行

```bash
python3 -m architect_lab orders
python3 -m architect_lab acid
python3 -m architect_lab events
python3 -m architect_lab cap
python3 -m architect_lab distributed
python3 -m architect_lab data
python3 -m architect_lab streaming
python3 -m architect_lab migration
python3 -m architect_lab security
python3 -m architect_lab planning
python3 -m architect_lab gof
python3 -m architect_lab.networking
```

CLIラボは一時ディレクトリを使い、終了時に消します。HTTPサーバーは現在のディレクトリに `orders.db` を作成します。

## Dockerでサービス間通信

Docker Engine/DesktopとCompose v2が必要です。

```bash
docker compose up --build -d
python3 scripts/smoke_http.py
curl -i http://127.0.0.1:8088/products
curl -i http://127.0.0.1:8088/products
```

Orders → Node Catalog の実通信と、NGINXの `X-Cache: MISS/HIT` を確認します。追加の手順は [INTEGRATIONS.md](docs/INTEGRATIONS.md) にまとめています。

```bash
docker compose down
```

`down` だけなら注文のnamed volumeは残ります。データ削除が必要なときだけ `docker compose down -v` を実行します。

## 実装の範囲

本教材は仕組みを追える小さな実装です。基本HTTP APIはローカル学習向けで、認証・決済・在庫確保を備えた本番サービスではありません。JWT/OAuth、CAP、イベントログ、document store、CDNの例は実装範囲を各ページに明記しています。

クラウドへのデプロイ、Jiraへの起票、Jenkins/Sonarの変更は自動実行しません。構成ファイルと具体例を収録しています。確認できた動作と未実行の外部環境は [VALIDATION.md](docs/VALIDATION.md) で区別しています。

項目構成の参考: [ByteByteGo — The Ultimate Software Architect Knowledge Map](https://bytebytego.com/guides/the-ultimate-software-architect-knowledge-map/)。コード、テストデータ、解説、Mermaid図はオリジナルです。スクリーンショットや製品ロゴは同梱していません。親リポジトリのMITライセンスに従います。
