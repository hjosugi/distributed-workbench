# Harbor Observer

複数のHarbor/Polycentric serverに同じHTTP pathを問い合わせ、応答の一致・欠落・遅延を調べる小さな運用ツールです。

## 実用ポイント

- `/status` のavailability比較
- `/blob/{digest}` のbytesとSHA-256比較
- 同じpathに複数variantがある場合のdivergence検出
- probe履歴のJSONL保存
- server URLは起動時設定、APIからは相対pathだけ受け付ける

## 起動

```bash
cp .env.example .env
set -a; . ./.env; set +a
go run ./cmd/harbor-observer
```

```bash
HARBOR_SERVERS='primary=https://server-a.example,backup=https://server-b.example' \
  go run ./cmd/harbor-observer
```

ブラウザで `http://localhost:8081` を開きます。

## API

```bash
curl -sS http://localhost:8081/api/probes \
  -H 'content-type: application/json' \
  -d '{"path":"/status"}'
```

```bash
curl -sS 'http://localhost:8081/api/probes?limit=10'
```

## 判定

- `healthy`: 2台以上が到達可能で、statusとSHA-256が一致
- `single-copy-risk`: 到達可能なserverが1台だけ
- `divergent`: 到達可能な応答が複数variant
- `unavailable`: すべて失敗

`MAX_BODY_BYTES` を超えるresponseはtruncatedとして表示されます。大きなblobの完全比較には値を増やしてください。
