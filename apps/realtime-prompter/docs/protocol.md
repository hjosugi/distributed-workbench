# WebSocket protocol

Endpoint: `ws://127.0.0.1:8766/ws`. One connection owns one session. There is no broadcast or resume protocol. Browser Origin must match the HTTP host. Non-browser clients may omit Origin. No authentication is provided: bind to loopback only.

## Client messages

| Message | Fields | Meaning |
|---|---|---|
| `transcript` | `text`: string, `is_final`: boolean | Inject the current segment; partial replaces, final commits |
| `start_audio` | `sample_rate`: integer, 8000–48000 | Reset transcript and create a mono PCM16LE recognizer |
| binary frame | At most 32768 bytes, nonempty and even length | Process PCM audio in order |
| `stop_audio` | — | Flush the recognizer and let generation finish |
| `reset` | — | Discard audio/transcript and cancel generation |
| `ping` | — | Confirm the connection is still usable during generation |

Text injection is rejected while audio is active. The WAV client and browser wait for `audio_started` before sending PCM. The browser allows at most four unacknowledged audio chunks; the WAV client allows one. A new microphone session resets the transcript.

## Server messages

| Message | Main fields | Meaning |
|---|---|---|
| `ready` | `generator`, `audio_ready`, `debounce_ms` | Session ready; audio readiness does not check Ollama |
| `transcript` | `revision`, `segment`, `confirmed`, `partial`, `text`, `is_final` | Replace the display state |
| `generation_start` | `revision` | Clear the answer and begin this generation |
| `generation_delta` | `revision`, `text`, `ttft_ms` | Append only if revision matches; TTFT is set on the first nonempty delta |
| `generation_done` | `revision` | This generation completed |
| `audio_started` | `sample_rate` | Audio recognizer initialized |
| `audio_ack` | `seq` | One binary audio frame was processed |
| `audio_stopped` | — | Pending audio finalized; generation may still be running |
| `reset` | `revision` | Clear client state |
| `pong` | — | Ping response |
| `error` | `message`, optional `revision` | Invalid input or provider failure; no silent fallback |

Revisions are monotonically increasing integers within one WebSocket connection. A fresh connection starts from zero. A final result advances the segment number. Revision is a generation identity, not an audio sequence number or a durable event offset.

Invalid application messages produce `error` and leave the socket usable. Frames above the transport limit can close the WebSocket before application validation. Ollama HTTP errors, error records, malformed JSON, timeouts, and EOF without `done:true` produce an error instead of `generation_done`. There are no automatic retries that could duplicate an answer.
