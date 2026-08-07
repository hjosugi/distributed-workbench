# PGPlay Recipes

PGliteでPostgreSQLをブラウザ内に起動し、Distributed Workbenchのschema patternを試すためのworkbenchです。

## pgplayとの違い

汎用DB clientを目指すのではなく、次のpatternをすぐ検証できるようにしています。

- NSQ transactional outbox / idempotent consumer / dead letter
- Harbor replica probe history
- order processing + outbox transaction
- table primary keyの簡易health check
- `EXPLAIN (FORMAT JSON)`
- SQL workspaceのURL共有

## 起動

```bash
npm install
npm run dev
```

ブラウザで `http://localhost:5173` を開きます。

## 保存先

Databaseは `idb://distributed-workbench` に保存されます。SQL editorの内容とhistoryはlocalStorageです。

## 操作

1. Recipeを選ぶ
2. `Reset + Apply recipe`を押す
3. SQLを編集して`Run SQL`
4. `Schema checks`でprimary key不足を確認
5. `Share SQL`で現在のSQLをURL hashへ入れる

共有URLにはSQL本文が含まれます。credentialやpersonal dataを入れないでください。
