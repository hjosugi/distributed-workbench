"""Send a local mono PCM16 WAV through the same WebSocket as the browser."""

import argparse
import asyncio
import json
import wave

from websockets.asyncio.client import connect


async def until(ws, expected):
    async with asyncio.timeout(130):
        while True:
            event = json.loads(await ws.recv())
            if event["type"] not in {"audio_ack", "pong"}:
                print(json.dumps(event, ensure_ascii=False), flush=True)
            if event["type"] == "error":
                raise RuntimeError(event["message"])
            if event["type"] == expected:
                return event


async def main(path, port):
    with wave.open(path, "rb") as wav:
        if wav.getnchannels() != 1 or wav.getsampwidth() != 2 or wav.getcomptype() != "NONE":
            raise ValueError("WAV must be mono, uncompressed PCM16")
        rate = wav.getframerate()
        if not 8000 <= rate <= 48000:
            raise ValueError("WAV sample rate must be 8000..48000 Hz")
        async with connect(f"ws://127.0.0.1:{port}/ws", max_size=65536, proxy=None) as ws:
            await until(ws, "ready")
            await ws.send(json.dumps({"type": "start_audio", "sample_rate": rate}))
            await until(ws, "audio_started")
            while pcm := wav.readframes(rate // 10):
                await ws.send(pcm)
                await until(ws, "audio_ack")
                await asyncio.sleep(0.1)
            await ws.send(json.dumps({"type": "stop_audio"}))
            await until(ws, "audio_stopped")
            # A silent WAV may not produce any generation; no completion is implied.
            print("Audio finalized. Listening for remaining output for up to 10 seconds.")
            try:
                async with asyncio.timeout(10):
                    await until(ws, "generation_done")
            except TimeoutError:
                print("No completion in 10 seconds (silence or a slow model).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wav")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    asyncio.run(main(args.wav, args.port))
