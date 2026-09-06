# 検証記録

確認日：2026-09-06。以下は初回追加時に、この開発環境で実行した範囲です。依存パッケージ・モデルの準備とGitHubへの送信はオンラインで行いました。実行中の音声認識とアプリ内の生成デモはローカル処理です。

| 検証 | 結果 |
|---|---|
| Python 3.12.13 / `python -m pytest -q` | 25 passed |
| Node.js 24.19.0 / `node --test tests/state.test.mjs` | 2 passed |
| `python -m pip check` | 依存パッケージの整合性確認 |
| FastAPIとWebSocket | 部分結果、確定、ping、不正JSON、不正PCM、Origin拒否、セッション分離を検証 |
| キャンセル | 実行中のasync generatorを終了し、修正後に旧revisionを配信しないことを検証 |
| Ollama adapter | HTTP requestのstream指定、NDJSON断片、HTTPエラー、error record、壊れたJSON、途中切断をローカルmockで検証 |
| PCM変換 | clipping、16-bit little-endian、末尾flush、flush後の停止を検証 |
| 日本語Vosk | `vosk-model-small-ja-0.22` のロードと48 kHz無音PCMの受付・final flushを実行 |
| 英語Voskの実音声経路 | 公式sample WAV → WebSocket → Vosk → テンプレート生成 → WebSocketを実行 |
| ブラウザE2E | GitHub Actionsで成功。部分結果の修正、final、生成中止、HTML文字列の無害な表示、390px幅、外部HTTP要求なしを確認。開発環境でのChromium取得はタイムアウト |
| Ollama実モデル推論 | この環境ではOllamaランタイム未導入のため未検証 |
| 実マイク・日本語認識精度 | 未検証。無音受付の確認は日本語の認識精度確認ではない |

英語音声の経路では、文字起こしイベント16件、生成開始16件、生成断片204件、生成完了4件を観測しました。途中の生成が置き換えられるため、開始と完了の数は一致しません。これらの件数は負荷やタイミングに依存し、性能保証やテストの固定期待値ではありません。

最初の確定文字起こしは `one zero zero zero one` でした。後続には誤認識もあり、音声認識結果の正確性までは保証しません。使用した音声は [Voskの公式test.wav](https://github.com/alphacep/vosk-api/blob/master/python/example/test.wav) です。この音声ファイルとモデルのバイナリはリポジトリに再配布しません。

取得したモデルZIPのSHA-256：

| モデル | 取得ファイルのSHA-256 |
|---|---|
| `vosk-model-small-ja-0.22` | `efa092d280153a77615e9e0c7d7283e93e600de3d19d3bec686c57ef19d52eac` |
| `vosk-model-small-en-us-0.15` | `30f26242c4eb449f948e42cb302dd7a686cb29a3423a8367f99ff41780942498` |

GitHub Actionsの `realtime-prompter` workflowはモデル不要のテストとブラウザE2Eを実行します。Vosk・OllamaのモデルはCIで自動取得しません。実モデルのテスト結果と、adapterをmockで確認した結果は区別してください。

## GitHub Actionsの結果

実装commit `05abdab4bd532c91522019d3b3174239b4f8377e` で次のworkflowが成功しました。

- [realtime-prompter：Python・Node・Chromium E2E](https://github.com/hjosugi/distributed-workbench/actions/runs/34026501254)
- [既存ci](https://github.com/hjosugi/distributed-workbench/actions/runs/34026501097)
- [依存グラフ更新](https://github.com/hjosugi/distributed-workbench/actions/runs/34026502542)
