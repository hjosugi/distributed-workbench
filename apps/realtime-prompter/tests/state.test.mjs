import assert from "node:assert/strict";
import test from "node:test";
import vm from "node:vm";
import { readFileSync } from "node:fs";
import { initialState, reduce } from "../static/state.mjs";

test("corrections replace text and reject stale deltas and completion", () => {
  let state = initialState();
  state = reduce(state, { type: "transcript", revision: 1, confirmed: "", partial: "高温", is_final: false });
  state = reduce(state, { type: "generation_delta", revision: 1, text: "old", ttft_ms: 20 });
  state = reduce(state, { type: "transcript", revision: 2, confirmed: "", partial: "交通", is_final: false });
  assert.equal(state.answer, "");
  state = reduce(state, { type: "generation_delta", revision: 1, text: "stale" });
  state = reduce(state, { type: "generation_done", revision: 1 });
  assert.equal(state.status, "生成待ち");
  state = reduce(state, { type: "generation_delta", revision: 2, text: "new", ttft_ms: 40 });
  assert.equal(state.answer, "new");
  assert.equal(state.partial, "交通");
  state = reduce(state, { type: "reset", revision: 3 });
  assert.equal(state.answer, "");
  assert.equal(reduce(state, { type: "generation_delta", revision: 2, text: "late" }).answer, "");
});

test("worklet emits clipped little-endian PCM and flushes the tail", () => {
  const messages = [];
  let Processor;
  const context = vm.createContext({
    AudioWorkletProcessor: class { constructor() { this.port = { postMessage: (data) => messages.push(data) }; } },
    registerProcessor: (name, cls) => { assert.equal(name, "pcm-capture"); Processor = cls; },
  });
  vm.runInContext(readFileSync(new URL("../static/pcm-worklet.js", import.meta.url), "utf8"), context);
  const processor = new Processor();
  processor.process([[new Float32Array([-2, -1, 0, 1, 2])]]);
  assert.equal(messages.length, 0);
  processor.port.onmessage({ data: "flush" });
  const view = new DataView(messages[0]);
  assert.deepEqual(Array.from({ length: 5 }, (_, i) => view.getInt16(i * 2, true)), [-32768, -32768, 0, 32767, 32767]);
  assert.equal(messages[1], "flushed");
  processor.process([[new Float32Array(5000)]]);
  assert.equal(messages.length, 2);
});
