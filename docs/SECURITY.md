# Security Notes

## Harbor Observer

- Probe先は起動時に設定したserverだけです。
- APIから受け取るのは相対pathだけで、schemeとhostを拒否します。
- response bodyは`MAX_BODY_BYTES`（既定8 MiB）まで読み、超過分は`truncated`として切り捨てます。
- productionではdashboardへauthenticationを追加してください。

## NSQ sample

- demo stackはTLS/Authなしです。public networkへ公開しないでください。
- job payloadにはsecretを入れないでください。
- file-backed storesはsingle-process前提です。
- productionではNSQ TLS/Auth、disk encryption、retention、DLQ access controlを設定してください。

## PGPlay Recipes

- SQLは利用者のbrowser内で実行されます。
- URL共有を使うとSQLがURL hashに入ります。credentialやpersonal dataを含めないでください。
- browser storageを消すとdatabaseも消えます。
