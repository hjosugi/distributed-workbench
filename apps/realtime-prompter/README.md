# Local Realtime Prompter

音声の **部分文字起こし → ストリーミング生成 → WebSocketによる画面更新** を、1台のPCで試す教材です。AWSアカウント、APIキー、クラウド推論は不要です。

独立した分散処理サンプルとして `distributed-workbench/apps` に収録しています。教材サイトの画像・設問文は同梱せず、同じ処理パターンを独自のコードと架空の発言で実装しています。

## まず動かす：モデル不要のデモ

Python 3.12、ブラウザを用意します。以下はリポジトリのルートから実行します。

```bash
cd apps/realtime-prompter
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn prompter.app:app --host 127.0.0.1 --port 8766 --ws websockets-sansio --ws-max-size 32768
```

Windows PowerShellでは、activateの代わりに `.venv\Scripts\Activate.ps1` を使います。

[http://127.0.0.1:8766](http://127.0.0.1:8766) を開き、「デモを再生」を押します。

1. 「今日は東京の高温について」という途中の発言が届く。
2. 固定テンプレートの生成結果が少しずつ表示される。
3. 「高温」が「交通」に修正される。
4. 古い生成を中止し、新しい文字起こしで表示を更新する。
5. 確定結果と次の文をつなぐ。イベント欄でrevisionの推移を確認できる。

**デモは音声認識・LLMを模擬します。WebSocket、キャンセル、画面更新は実装を動かしています。** 音声を鳴らすデモではありません。「部分結果を送信」「発言を確定」でも試せます。音声入力と手動入力は同時に使いません。

初回の依存パッケージ取得にはインターネットが必要です。インストール後は上の起動コマンドだけでオフライン動作します。

## 実際のマイク入力を使う

停止中のアプリと同じ仮想環境で実行します。

```bash
python -m pip install -r requirements-audio.txt
python scripts/download_model.py --language ja
export VOSK_MODEL_PATH="$PWD/models/vosk-model-small-ja-0.22"
python -m uvicorn prompter.app:app --host 127.0.0.1 --port 8766 --ws websockets-sansio --ws-max-size 32768
```

PowerShellでの設定：

```powershell
$env:VOSK_MODEL_PATH = (Resolve-Path models/vosk-model-small-ja-0.22).Path
```

ブラウザで「マイクを開始」を押し、マイク使用を許可します。日本語の小型Voskモデルは公式一覧で48MBです。モデルは初回だけダウンロードし、Gitには含めません。ダウンロードスクリプトは取得ファイルのSHA-256を表示します。配布元の署名検証を代替するものではありません。

音声はAudioWorkletで **mono PCM16 little-endian** に変換し、最大4096サンプルずつ送ります。AudioContextの実際のsample rate（8〜48 kHz）をVoskへ渡します。WebM/OpusをPCMとして渡したり、端末が必ず16 kHzになると仮定したりしません。`getUserMedia` による音声取得だけを使い、外部認識サービスにつながる可能性のあるWeb Speech APIは使いません。

「音声・デモを停止」はマイクを解放し、残った音声を確定します。生成は完了まで続きます。「クリア・生成を中止」は文字起こしと生成を破棄します。

## 実際のローカルLLMも使う

1. [Ollama公式手順](https://docs.ollama.com/)から、PCのOSに合うOllamaをインストールします。
2. Ollamaのクラウド機能を無効にして起動します。既存サービスを使う場合は、**そのサービス側**に同じ設定を適用して再起動します。

```bash
OLLAMA_NO_CLOUD=1 ollama serve
```

3. 別の端末で、小型のローカルモデルを初回だけ取得します。

```bash
ollama pull qwen3:0.6b
```

4. アプリを停止し、以下の設定で再起動します。

```bash
export PROMPTER_LLM=ollama
export OLLAMA_MODEL=qwen3:0.6b
export VOSK_MODEL_PATH="$PWD/models/vosk-model-small-ja-0.22"
python -m uvicorn prompter.app:app --host 127.0.0.1 --port 8766 --ws websockets-sansio --ws-max-size 32768
```

PowerShellでは各変数を `$env:PROMPTER_LLM = "ollama"` の形式で設定します。Ollamaを起動する端末にも `$env:OLLAMA_NO_CLOUD = "1"` を設定してください。

アプリの生成先は **`http://127.0.0.1:11434/api/generate` に固定**。HTTPプロキシ環境変数とリダイレクトを使いません。クラウド指定を含むモデル名も拒否します。モデル名の検査だけでクラウド利用を完全に抑止できるわけではないので、Ollama側の `OLLAMA_NO_CLOUD=1` も必要です。

モデルと依存パッケージを準備した後はネットワークを切って実行できます。認識精度、最初のトークンまでの時間、生成の質はPC・モデル・入力に依存します。`qwen3:0.6b` は動作確認用の小型例です。高品質な日本語や低遅延を保証するモデル選定ではありません。

このアプリは発言の要約と確認質問を生成します。ニュースの検索、事実の検証、最新情報の取得は行いません。

## 元のAWS構成との対応

| AWS構成の役割 | ローカル実装 | 確認できること |
|---|---|---|
| 音声ストリーム | ブラウザAudioWorklet / WAVクライアント | 音声を小さいチャンクで送る |
| Amazon Transcribe | Vosk `AcceptWaveform` / `PartialResult` / `Result` | 部分結果の修正と確定結果 |
| AWS Lambdaの処理 | FastAPI + `Session` | 入力受付、確定文の保持、生成タスクの制御 |
| Bedrock `InvokeModelWithResponseStream` | Ollama `/api/generate` のNDJSON | 生成の完了を待たずに断片を配信 |
| API Gateway WebSocket API | FastAPI `/ws` | 音声・操作の受信と生成結果のpush |
| プロンプター | ローカルHTML/CSS/JavaScript | 途中の生成結果とrevisionを表示 |

APIの互換エミュレーターではなく、処理パターンの再現です。特にVoskのpartialにはTranscribeのtoken-level `Stable` フラグ相当を実装していません。またLambdaの通常の戻り値が自動でWebSocketに届くわけではありません。AWSでは接続IDを管理し、バックエンドからManagement APIでメッセージを送る処理が必要です。[詳細と図](docs/architecture.md)

## 設定

| 変数 | 既定値 | 用途 |
|---|---|---|
| `PROMPTER_LLM` | `demo` | `demo` または `ollama` |
| `OLLAMA_MODEL` | `qwen3:0.6b` | あらかじめ取得したローカルモデル |
| `VOSK_MODEL_PATH` | 未設定 | 展開済みVoskモデル。未設定ならテキスト専用 |
| `DEBOUNCE_MS` | `350` | 部分結果が落ち着くまでの待ち時間。0〜3000 |

確定結果はdebounceを待ちません。途中の結果が350ms未満で変わり続けると、生成の開始は遅れます。これは要求のたびに重い推論を起動しないための教材上の選択です。`DEBOUNCE_MS=0` と比較できます。生成中でも新しい文字起こしを受け付けます。

## 検証する

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
node --test tests/state.test.mjs
```

Node.js 24はブラウザ状態管理とPCM変換のテストにだけ必要です。通常のPythonサーバー起動には不要です。

ブラウザの操作テスト：

```bash
npm ci
npx playwright install chromium --only-shell
npm run test:browser
```

`test:browser` は別ポート8799でモデル不要サーバーを起動し、終了時に停止します。Linuxでブラウザのシステム依存が足りない場合は、Playwright公式手順の `npx playwright install --with-deps chromium --only-shell` を利用します。

手元の音声ファイルでも、ブラウザと同じ経路を試せます。Voskを設定したサーバーを先に起動してください。

```bash
python scripts/stream_wav.py /path/to/mono-pcm16.wav
```

WAVは非圧縮mono PCM16、8〜48 kHzが必要です。日本語モデルには日本語音声を使います。英語は `python scripts/download_model.py --language en` でモデルを準備し、`VOSK_MODEL_PATH` を `models/vosk-model-small-en-us-0.15` に変えて再起動します。

テスト範囲と実行結果は [docs/validation.md](docs/validation.md)、メッセージ仕様は [docs/protocol.md](docs/protocol.md)、面接用の短い説明は [docs/interview.md](docs/interview.md) にまとめています。

## 困ったとき

| 症状 | 確認すること |
|---|---|
| マイクボタンが無効 | `VOSK_MODEL_PATH` を設定してサーバーを再起動したか |
| マイクが使えない | `http://127.0.0.1:8766` / localhostで開き、ブラウザの権限とOS設定を確認 |
| 生成エラー | Ollamaが起動しているか、`ollama list` にモデルがあるか |
| デモの文章しか出ない | サーバー起動前に `PROMPTER_LLM=ollama` を設定したか |
| 文字が出るまで遅い | 初回モデルロード、CPU負荷、debounce、音声の区切りを確認 |
| 音声が停止する | 未処理の音声が4チャンクを超えた。PC負荷を下げ、再開する |
| 接続が切れた | 「再接続」。文字起こしの自動復元はしない |

サーバーはloopbackにbindします。1接続が1セッションを持ち、他のタブには配信しません。外部公開、認証、複数PCへの共有、永続化は対象外です。

## 公式資料

確認日：2026-09-06。API名・パッケージは確認時の実在するものを使用しています。

- [Amazon Transcribe: streaming and partial results](https://docs.aws.amazon.com/transcribe/latest/dg/streaming-partial-results.html)
- [Bedrock: InvokeModelWithResponseStream](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModelWithResponseStream.html)
- [API Gateway: WebSocket APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api-overview.html)
- [Voskモデルとライセンス](https://alphacephei.com/vosk/models)、[Pythonの公式サンプル](https://github.com/alphacep/vosk-api/blob/master/python/example/test_simple.py)
- [Ollama Generate API](https://docs.ollama.com/api/generate)、[クラウド機能の無効化](https://docs.ollama.com/faq#how-do-i-disable-ollama-cloud-features)、[qwen3:0.6b](https://ollama.com/library/qwen3:0.6b)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)、[HTTPX async streaming](https://www.python-httpx.org/async/)
- [MDN getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)、[AudioContext](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext)
