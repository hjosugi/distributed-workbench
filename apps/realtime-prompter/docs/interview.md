# Design a Realtime Speech Prompter

## 30-sec summary

I stream audio to speech recognition. It returns partial and final transcripts. I start generation from partial text and stream the output to the browser over WebSocket. When the transcript changes, I cancel the old request. Each update has a revision ID, so the browser ignores stale output.

## Clarifying questions

- How many speakers and viewers do we need?
- What is the target time to the first useful hint?
- Can we display provisional results?
- Must speech and inference stay on the device?
- Do viewers need to recover missed events after reconnecting?

## Requirements

- Accept continuous audio and show partial transcripts.
- Show generated hints before generation finishes.
- Support corrections, cancellation, and connection failures.
- Keep audio and inference local for this implementation.
- Bound memory and pending work.

## High-level design

The browser sends PCM audio and control messages over WebSocket. Vosk returns partial transcripts. A session manager stores confirmed text and the current partial text. Ollama streams generated text. The session manager adds revision IDs and pushes events to the browser.

## Deep dive 1

Partial transcripts can change. I replace the current partial text instead of appending it. Final text moves into the confirmed buffer. I bound the prompt context to the latest 2,000 characters.

## Deep dive 2

Each transcript change creates a new revision. I cancel the old generation task and close its HTTP stream. Both the server and client check the revision before accepting a delta. This prevents old and new answers from mixing.

## Deep dive 3

I debounce partial updates and process final updates immediately. Audio acknowledgements track pending chunks. If the browser gets more than four chunks behind, I stop input and show an error. A slow model can still delay useful output. I measure time to the first output separately from speech recognition latency.

## Tradeoffs

Earlier output reduces waiting, but it uses less stable input. Debounce reduces wasted inference, but delays output during continuous changes. Local inference keeps data on the device, but performance depends on the user's hardware. This lab uses one connection per session; a larger service needs routing, admission control, and shared session metadata.

## Failure cases

- A revised transcript invalidates old output.
- A disconnected browser cancels its generation task.
- A missing model produces an explicit error.
- A truncated model stream is not reported as success.
- Slow audio processing stops capture instead of growing an unlimited queue.
- Reconnecting starts a new session; there is no durable replay.

## 2-min English answer

This system helps a presenter while they are speaking. I first confirm the latency target and whether we can show provisional results.

The browser captures audio and sends small PCM chunks over WebSocket. A speech recognizer returns partial transcripts before the speaker finishes. I store confirmed text separately from the current partial text because partial text can change.

The session manager starts a streaming model request. As text arrives, it sends small output events to the browser. The browser can display the first useful hint before generation finishes.

The main correctness problem is stale output. A transcript correction creates a new revision. I cancel the old generation and attach the revision to each output event. The browser only accepts events for its current revision.

The main performance problem is repeated work. I debounce partial changes and process final text immediately. I also bound the context size and the number of audio chunks waiting for processing. If the client falls behind, it stops audio and tells the user.

For this local implementation, I use Vosk, FastAPI, and Ollama. No cloud inference is required. In a larger service, I would add authentication, admission control, connection routing, and a replay policy. I would measure speech recognition delay, time to the first model output, and the rate of cancelled generations separately.
