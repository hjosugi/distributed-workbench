# プロジェクトの役割

## 1. Harbor Observer

### 解決する問題

Harborでは、同じ利用者のデータが複数サーバに存在し得ます。しかし、運用者から見ると「どのサーバが落ちているか」「同じblobが同じbytesを返すか」が分かりにくいです。

### 実装したもの

- 複数サーバへ並列GET
- status、latency、body size、SHA-256の比較
- 応答variant数とcoverageから状態を分類
- JSONLへのprobe履歴保存
- `/blob/{digest}` など任意の相対パスを検査
- browser dashboardとJSON API

### 独自性

単純なhealth checkではなく、content-addressed dataの一致まで確認します。Harborに限らず、複数replicaのHTTP object検査にも使えます。

## 2. NSQ Reliable Worker

### 解決する問題

NSQはat-least-once deliveryです。consumerは同じmessageを複数回受ける可能性があり、失敗時のretryやDLQもapplication側で設計する必要があります。

### 実装したもの

- durable JSONL outboxを持つJob API
- NSQ HTTP publish
- Go標準ライブラリだけで実装したNSQ V2 TCP consumer
- heartbeat、SUB、RDY、FIN、REQの処理
- processed logによるidempotency
- exponential retry
- max attempts後のDLQ publish
- Prometheus形式metrics
- PostgreSQLへ移行するためのmigration SQL

### 独自性

古い`tokio-nsq`へ依存せず、protocolの重要部分を小さな実装として読めます。同時に、実運用で必要なoutbox、idempotency、DLQを1つのsampleで確認できます。

## 3. PGPlay Recipes

### 解決する問題

outboxやidempotencyのschemaを試すたびにPostgreSQL containerを作るのは手間です。

### 実装したもの

- PGliteによるブラウザ内PostgreSQL
- IndexedDB永続化
- multi-statement SQL execution
- schema explorer
- result grid
- `EXPLAIN (FORMAT JSON)`
- workspace export/import
- SQLをURL hashへ入れる共有機能
- Harbor Observer、NSQ reliability向けrecipe

### 独自性

汎用SQL editorではなく、このモノレポ内のdistributed systems patternをその場で編集・検証するworkbenchです。

## 推奨する開発順

1. `docker compose up --build` で全体を動かす
2. NSQ APIへ失敗するjobを投入し、retryとDLQを見る
3. PGPlay Recipesでoutbox/idempotency schemaを変更する
4. Harbor serverを2台以上設定し、`/status` と `/blob/{digest}` を比較する
5. file-backed storeをPostgreSQL実装に置き換える

## Realtime Prompter

[`apps/realtime-prompter`](../apps/realtime-prompter/README.md) は、音声の部分文字起こしから生成を開始し、WebSocketでプロンプターを更新する独立したローカル教材です。

- Voskによる部分結果と確定結果、Ollamaによる生成ストリーム
- FastAPIの双方向WebSocket、PCM音声チャンクと制御メッセージ
- revisionによる古い生成結果の除外、キャンセル、debounce、音声backpressure
- モデル不要のデモ、テストデータ、API・状態管理・ブラウザテスト
- AWS構成との対応表と短い英語の面接回答

初回準備後はオフラインで動作します。既存Docker Composeと独立して起動し、AWSアカウントやAPIキーは使いません。
