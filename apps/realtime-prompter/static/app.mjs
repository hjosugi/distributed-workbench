import { initialState, reduce } from "./state.mjs";

const $ = (id) => document.getElementById(id);
let ws, state = initialState(), ready = false, audioReady = false, mic = null, micBusy = false;
let demoAbort = null, captureEpoch = 0, pendingAudio = 0, entries = [], counter = 0;
const waiters = new Map();

function notice(text, error = false) {
  $("notice").textContent = text;
  $("notice").classList.toggle("error", error);
}

function controls() {
  $("demo").disabled = !ready || !!mic || micBusy || !!demoAbort;
  $("mic").disabled = !ready || !audioReady || !!mic || micBusy || !!demoAbort;
  $("stop").disabled = !mic && !micBusy && !demoAbort;
  $("reset").disabled = !ready;
  $("partial-send").disabled = $("final-send").disabled = !ready || !!mic || micBusy || !!demoAbort;
}

function render() {
  $("confirmed").textContent = state.confirmed + (state.confirmed && state.partial ? " " : "");
  $("partial").textContent = state.partial;
  $("answer").textContent = state.answer || (state.revision ? "更新を待っています…" : "「デモを再生」で、生成結果が少しずつ届く様子を確認できます。");
  $("revision").textContent = state.revision;
  $("generation-state").textContent = state.status;
  $("transcript-state").textContent = state.partial ? "部分結果・修正あり" : state.confirmed ? "確定" : "待機";
  $("latency").textContent = state.ttft == null ? "—" : `${state.ttft} ms`;
}

function send(message) {
  if (!ready || ws.readyState !== WebSocket.OPEN) throw new Error("接続が切れています。再接続してください。");
  ws.send(JSON.stringify(message));
}

function waitFor(type) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => { waiters.delete(type); reject(new Error(`${type}: 応答がありません。`)); }, 10000);
    waiters.set(type, { resolve: (value) => { clearTimeout(timer); resolve(value); }, reject: (error) => { clearTimeout(timer); reject(error); } });
  });
}

function rejectWaiters(error) {
  for (const waiter of waiters.values()) waiter.reject(error);
  waiters.clear();
}

function connect() {
  ready = false;
  controls();
  $("connection").textContent = "接続中";
  $("reconnect").hidden = true;
  ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`);
  ws.onmessage = ({ data }) => {
    const event = JSON.parse(data);
    if (event.type === "ready") {
      ready = true; audioReady = event.audio_ready;
      state = initialState();
      $("connection").textContent = "ローカル接続中";
      $("mode").textContent = `${event.generator} / 音声 ${audioReady ? "準備完了" : "モデル未設定"}`;
      controls();
    }
    if (event.type === "audio_ack") { pendingAudio = Math.max(0, pendingAudio - 1); return; }
    if (event.type === "error") {
      notice(event.message, true);
      rejectWaiters(new Error(event.message));
    }
    const waiter = waiters.get(event.type);
    if (waiter) { waiters.delete(event.type); waiter.resolve(event); }
    state = reduce(state, event);
    render();
    counter++;
    entries.unshift(`${new Date().toLocaleTimeString()} ${JSON.stringify(event)}`);
    entries = entries.slice(0, 80);
    $("events").textContent = entries.join("\n");
    $("event-count").textContent = counter;
  };
  ws.onclose = () => {
    ready = false;
    demoAbort?.abort();
    rejectWaiters(new Error("接続が切れました。"));
    stopCapture(false).catch(() => {});
    state = { ...state, status: "切断" }; render();
    $("connection").textContent = "切断";
    $("reconnect").hidden = false;
    notice("接続が切れました。再接続すると新しいセッションになります。", true);
    controls();
  };
  ws.onerror = () => notice("ローカルサーバーへの接続に失敗しました。", true);
}

function delay(ms, signal) {
  return new Promise((resolve, reject) => {
    const abort = () => { clearTimeout(timer); reject(new DOMException("Aborted", "AbortError")); };
    const timer = setTimeout(() => { signal.removeEventListener("abort", abort); resolve(); }, ms);
    signal.addEventListener("abort", abort, { once: true });
    if (signal.aborted) abort();
  });
}

$("demo").onclick = async () => {
  demoAbort = new AbortController(); controls();
  const signal = demoAbort.signal;
  try {
    send({ type: "reset" });
    const response = await fetch("/demo", { signal });
    if (!response.ok) throw new Error("デモを読み込めませんでした。");
    notice("架空の発言を再生中。「高温」が「交通」に修正されます。デモ音声はありません。");
    for (const { after_ms, ...event } of await response.json()) {
      await delay(after_ms, signal); send(event);
    }
    notice("デモ再生が完了しました。最後の生成が続く間も、クリアで中止できます。");
  } catch (error) { if (error.name !== "AbortError") notice(error.message, true); }
  finally { demoAbort = null; controls(); }
};

async function startCapture() {
  const epoch = ++captureEpoch;
  micBusy = true; controls();
  let stream, context;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, echoCancellation: true }, video: false });
    if (epoch !== captureEpoch) { stream.getTracks().forEach((track) => track.stop()); return; }
    context = new AudioContext();
    if (context.sampleRate > 48000 || context.sampleRate < 8000) throw new Error("音声デバイスを8〜48 kHzに設定してください。");
    await context.audioWorklet.addModule("/static/pcm-worklet.js");
    await context.resume();
    if (epoch !== captureEpoch) throw new Error("マイク開始を中止しました。");
    const started = waitFor("audio_started");
    send({ type: "start_audio", sample_rate: context.sampleRate });
    await started;
    if (epoch !== captureEpoch) throw new Error("マイク開始を中止しました。");
    const source = context.createMediaStreamSource(stream);
    const node = new AudioWorkletNode(context, "pcm-capture");
    mic = { stream, context, source, node, flushing: false, flushed: null };
    pendingAudio = 0;
    node.port.onmessage = ({ data }) => {
      if (data === "flushed") { mic?.flushed?.(); return; }
      if (!ready || !mic || mic.discard) return;
      if (pendingAudio >= 4 || ws.bufferedAmount > 65536) {
        notice("音声処理が追いつかないため停止しました。PC負荷を下げて再開してください。", true);
        stopCapture(false).then(() => { if (ready) send({ type: "reset" }); }).catch(() => {});
        return;
      }
      pendingAudio++; ws.send(data);
    };
    source.connect(node); node.connect(context.destination);
    notice("マイク入力中。PCM音声をこのPCのVoskへ送り、途中の結果から生成します。");
  } catch (error) {
    stream?.getTracks().forEach((track) => track.stop());
    if (context && context.state !== "closed") await context.close();
    notice(error.message, true);
    if (ready) send({ type: "reset" });
  } finally { micBusy = false; controls(); }
}

async function stopCapture(finalize = true) {
  ++captureEpoch;
  const current = mic;
  if (!current) return;
  if (current.flushing) {
    if (!finalize) current.discard = true;
    return current.stopPromise;
  }
  current.flushing = true;
  current.discard = !finalize;
  current.stopPromise = (async () => {
    current.stream.getTracks().forEach((track) => track.stop());
    if (finalize && ready) {
      await new Promise((resolve) => {
        const timer = setTimeout(resolve, 500);
        current.flushed = () => { clearTimeout(timer); resolve(); };
        current.node.port.postMessage("flush");
      });
    }
    current.source.disconnect(); current.node.disconnect();
    await current.context.close();
    if (mic === current) mic = null;
    pendingAudio = 0;
    if (!current.discard && ready) send({ type: "stop_audio" });
    controls();
  })();
  return current.stopPromise;
}

$("mic").onclick = startCapture;
$("stop").onclick = async () => {
  demoAbort?.abort();
  await stopCapture();
  notice("入力を停止しました。生成も中止する場合はクリアしてください。");
};
$("reset").onclick = async () => {
  demoAbort?.abort();
  await stopCapture(false);
  send({ type: "reset" });
  notice("セッションをクリアしました。");
};
$("reconnect").onclick = connect;
function submitText(is_final) {
  try {
    send({ type: "transcript", text: $("text-input").value, is_final });
    if (is_final) $("text-input").value = "";
    notice(is_final ? "発言を確定しました。" : "途中の文を送りました。書き換えて再送すると修正できます。");
  } catch (error) { notice(error.message, true); }
}
$("partial-send").onclick = () => submitText(false);
$("text-form").onsubmit = (event) => { event.preventDefault(); submitText(true); };
window.addEventListener("pagehide", () => { mic?.stream.getTracks().forEach((track) => track.stop()); ws?.close(); });
connect();
