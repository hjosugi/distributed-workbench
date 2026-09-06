class PCMProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.samples = new Float32Array(4096);
    this.used = 0;
    this.running = true;
    this.port.onmessage = ({ data }) => {
      if (data === "flush") {
        this.running = false;
        this.flush();
        this.port.postMessage("flushed");
      }
    };
  }

  flush() {
    if (!this.used) return;
    const buffer = new ArrayBuffer(this.used * 2);
    const view = new DataView(buffer);
    for (let i = 0; i < this.used; i++) {
      const value = Math.max(-1, Math.min(1, this.samples[i]));
      view.setInt16(i * 2, value < 0 ? value * 32768 : value * 32767, true);
    }
    this.port.postMessage(buffer, [buffer]);
    this.used = 0;
  }

  process(inputs) {
    if (!this.running) return true;
    const channel = inputs[0]?.[0];
    if (channel) {
      for (const value of channel) {
        this.samples[this.used++] = value;
        if (this.used === this.samples.length) this.flush();
      }
    }
    return true;
  }
}
registerProcessor("pcm-capture", PCMProcessor);
