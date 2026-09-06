"""Serve a local-only UI, PCM audio input, and bidirectional events."""

import asyncio
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .providers import DemoGenerator, OllamaGenerator, VoskRecognizer, load_vosk_model
from .session import Session

ROOT = Path(__file__).resolve().parent.parent


def create_app(generator=None, recognizer_factory=None, debounce_ms=None):
    @asynccontextmanager
    async def lifespan(app):
        mode = os.getenv("PROMPTER_LLM", "demo")
        if mode not in {"demo", "ollama"}:
            raise ValueError("PROMPTER_LLM must be demo or ollama")
        app.state.generator = generator if generator is not None else (
            OllamaGenerator(os.getenv("OLLAMA_MODEL", "qwen3:0.6b"))
            if mode == "ollama" else DemoGenerator()
        )
        app.state.recognizer_factory = recognizer_factory
        path = os.getenv("VOSK_MODEL_PATH", "")
        if path and recognizer_factory is None:
            model = await asyncio.to_thread(load_vosk_model, path)
            app.state.recognizer_factory = lambda rate: VoskRecognizer(model, rate)
        app.state.debounce_ms = (
            int(os.getenv("DEBOUNCE_MS", "350")) if debounce_ms is None else debounce_ms
        )
        if not 0 <= app.state.debounce_ms <= 3000:
            raise ValueError("DEBOUNCE_MS must be between 0 and 3000")
        yield

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver"])

    @app.get("/")
    async def index():
        return FileResponse(ROOT / "static/index.html")

    @app.get("/health")
    async def health():
        return {
            "status": "ok", "generator": app.state.generator.name,
            "audio_ready": app.state.recognizer_factory is not None,
            "debounce_ms": app.state.debounce_ms,
        }

    @app.get("/demo")
    async def demo():
        return json.loads((ROOT / "fixtures/transcripts.json").read_text(encoding="utf-8"))

    @app.websocket("/ws")
    async def websocket(ws: WebSocket):
        # Browser WebSockets must come from this local UI. CLI clients omit Origin.
        origin = ws.headers.get("origin")
        if origin and origin != f"http://{ws.headers.get('host')}":
            await ws.close(code=1008)
            return
        await ws.accept()
        lock = asyncio.Lock()

        async def send(event):
            async with lock:
                try:
                    await asyncio.wait_for(ws.send_json(event), timeout=5)
                except (WebSocketDisconnect, RuntimeError, OSError, TimeoutError):
                    # A disconnected or stalled browser must not leave a task alive.
                    raise asyncio.CancelledError

        session = Session(send, app.state.generator, app.state.debounce_ms)
        recognizer = None
        audio_seq = 0
        try:
            await send({"type": "ready", **await health()})
            while True:
                packet = await ws.receive()
                if packet["type"] == "websocket.disconnect":
                    break
                try:
                    if packet.get("bytes") is not None:
                        pcm = packet["bytes"]
                        if recognizer is None:
                            raise ValueError("先に start_audio を送信してください。")
                        if not pcm or len(pcm) > 32768 or len(pcm) % 2:
                            raise ValueError("PCMは偶数byte、1〜32768byteのmono PCM16LEです。")
                        text, final = await asyncio.to_thread(recognizer.feed, pcm)
                        await session.update(text, final)
                        audio_seq += 1
                        await send({"type": "audio_ack", "seq": audio_seq})
                        continue
                    raw = packet.get("text", "")
                    if len(raw) > 8192:
                        raise ValueError("JSON message too large")
                    message = json.loads(raw)
                    if not isinstance(message, dict):
                        raise ValueError("JSON object required")
                    kind = message.get("type")
                    if kind == "transcript":
                        if recognizer is not None:
                            raise ValueError("音声入力を停止してからテキストを送信してください。")
                        text = message.get("text")
                        final = message.get("is_final", False)
                        if not isinstance(text, str) or len(text) > 2000 or type(final) is not bool:
                            raise ValueError("text: string <= 2000 chars; is_final: boolean")
                        await session.update(text, final)
                    elif kind == "start_audio":
                        rate = message.get("sample_rate")
                        if type(rate) is not int or not 8000 <= rate <= 48000:
                            raise ValueError("sample_rate must be an integer from 8000 to 48000")
                        if app.state.recognizer_factory is None:
                            raise ValueError("音声入力にはVOSK_MODEL_PATHを指定して再起動してください。")
                        if recognizer is not None:
                            raise ValueError("音声入力はすでに開始しています。")
                        await session.reset()
                        recognizer = await asyncio.to_thread(app.state.recognizer_factory, rate)
                        audio_seq = 0
                        await send({"type": "audio_started", "sample_rate": rate})
                    elif kind == "stop_audio":
                        if recognizer is not None:
                            text, final = await asyncio.to_thread(recognizer.finish)
                            recognizer = None
                            await session.update(text, final)
                        await send({"type": "audio_stopped"})
                    elif kind == "reset":
                        recognizer = None
                        await session.reset()
                    elif kind == "ping":
                        await send({"type": "pong"})
                    else:
                        raise ValueError("Unknown message type")
                except (ValueError, TypeError, RuntimeError) as exc:
                    await send({"type": "error", "message": str(exc)[:300]})
        except WebSocketDisconnect:
            pass
        finally:
            await session.close()

    app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
    return app


app = create_app()
