import asyncio
import json

import httpx
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from prompter.app import create_app
from prompter.providers import OllamaGenerator
from prompter.session import Session


class FastGenerator:
    name = "test"

    async def stream(self, text):
        yield "hint: "
        yield text


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("VOSK_MODEL_PATH", raising=False)
    with TestClient(create_app(generator=FastGenerator(), debounce_ms=0)) as client:
        yield client


def receive(ws, kind):
    events = []
    for _ in range(50):
        event = ws.receive_json()
        events.append(event)
        if event["type"] == kind:
            return events
    raise AssertionError(f"Missing {kind}: {events}")


def test_http_and_bidirectional_stream(client):
    assert client.get("/").status_code == 200
    assert client.get("/static/app.mjs").status_code == 200
    assert client.get("/health").json()["audio_ready"] is False
    assert len(client.get("/demo").json()) == 6
    with client.websocket_connect("/ws") as ws:
        assert ws.receive_json()["type"] == "ready"
        ws.send_json({"type": "transcript", "text": "交通", "is_final": False})
        events = receive(ws, "generation_done")
        assert events[0]["partial"] == "交通"
        assert "".join(e["text"] for e in events if e["type"] == "generation_delta") == "hint: 交通"
        assert events[2]["ttft_ms"] is not None
        ws.send_json({"type": "ping"})
        assert ws.receive_json() == {"type": "pong"}


@pytest.mark.parametrize("bad", [[], None, {"type": "wat"},
    {"type": "transcript", "text": 3},
    {"type": "transcript", "text": "x", "is_final": "false"},
    {"type": "transcript", "text": "x" * 2001},
    {"type": "start_audio", "sample_rate": True},
    {"type": "start_audio", "sample_rate": 96000},
    {"type": "start_audio", "sample_rate": 16000}])
def test_invalid_input_keeps_connection_usable(client, bad):
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.send_json(bad)
        assert ws.receive_json()["type"] == "error"
        ws.send_text("not json")
        assert ws.receive_json()["type"] == "error"
        ws.send_bytes(b"\0\0")
        assert ws.receive_json()["type"] == "error"
        ws.send_json({"type": "ping"})
        assert ws.receive_json()["type"] == "pong"


def test_origin_and_host(client):
    assert client.get("/", headers={"host": "attacker.example"}).status_code == 400
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws", headers={"origin": "https://attacker.example"}):
            pass
    with client.websocket_connect("/ws", headers={"origin": "http://testserver"}) as ws:
        assert ws.receive_json()["type"] == "ready"


def test_connections_are_isolated(client):
    with client.websocket_connect("/ws") as a, client.websocket_connect("/ws") as b:
        a.receive_json(); b.receive_json()
        a.send_json({"type": "transcript", "text": "private A", "is_final": True})
        receive(a, "generation_done")
        b.send_json({"type": "transcript", "text": "B", "is_final": True})
        assert receive(b, "generation_done")[0]["confirmed"] == "B"


def test_correction_finalization_and_reset():
    async def scenario():
        events = []
        async def send(event): events.append(event)
        session = Session(send, FastGenerator(), debounce_ms=500)
        await session.update("高温", False)
        await session.update("交通", False)
        await session.update("交通です。", True)
        await session.task
        assert [e["revision"] for e in events if e["type"] == "generation_start"] == [3]
        assert session.confirmed == "交通です。"
        await session.update("続き", False)
        await session.update("", True)
        await session.task
        assert session.confirmed == "交通です。"
        assert session.partial == ""
        await session.reset()
        assert not session.confirmed and not session.partial
        assert session.task is None
        await session.close()
    asyncio.run(scenario())


def test_cancel_inflight_and_disconnect_closes_provider():
    async def scenario():
        entered = asyncio.Event()
        released = asyncio.Event()
        events = []
        class BlockingGenerator:
            async def stream(self, text):
                try:
                    yield text
                    entered.set()
                    await asyncio.Event().wait()
                    yield "stale"
                finally:
                    released.set()
        async def send(event): events.append(event)
        session = Session(send, BlockingGenerator(), debounce_ms=0)
        await session.update("old", True)
        await asyncio.wait_for(entered.wait(), 1)
        await session.update("new", False)
        await asyncio.wait_for(released.wait(), 1)
        after_new = events[next(i for i, e in enumerate(events) if e.get("revision") == 2):]
        assert not any(e.get("revision") == 1 for e in after_new)
        await session.close()
        assert session.task is None
    asyncio.run(scenario())


def test_duplicate_partial_and_bounded_context():
    async def scenario():
        events = []
        async def send(event): events.append(event)
        session = Session(send, FastGenerator(), debounce_ms=500)
        await session.update("hello", False)
        await session.update("hello", False)
        assert session.revision == 1
        await session.update("x" * 1900, True)
        await session.update("y" * 1900, True)
        assert len(session.confirmed) == 2000
        await session.close()
    asyncio.run(scenario())


def test_audio_frames_and_flush(monkeypatch):
    monkeypatch.delenv("VOSK_MODEL_PATH", raising=False)
    frames = []
    class Recognizer:
        def feed(self, pcm):
            frames.append(pcm)
            return "途中", False
        def finish(self): return "確定した発言", True
    def factory(rate):
        assert rate == 48000
        return Recognizer()
    with TestClient(create_app(FastGenerator(), factory, 0)) as client:
        with client.websocket_connect("/ws") as ws:
            assert ws.receive_json()["audio_ready"]
            ws.send_json({"type": "start_audio", "sample_rate": 48000})
            receive(ws, "audio_started")
            ws.send_bytes(b"x")
            assert ws.receive_json()["type"] == "error"
            ws.send_bytes(b"\0\0" * 64)
            events = receive(ws, "audio_ack")
            assert any(e.get("partial") == "途中" for e in events)
            ws.send_json({"type": "stop_audio"})
            events = receive(ws, "audio_stopped")
            final = next(e for e in events if e["type"] == "transcript")
            assert final["confirmed"] == "確定した発言"
    assert frames == [b"\0\0" * 64]


def test_ollama_stream_request_and_chunks():
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(200, text='{"response":"交通","done":false}\n\n{"response":"です","done":true}\n')
    async def scenario():
        provider = OllamaGenerator("qwen3:0.6b", httpx.MockTransport(handler))
        assert [s async for s in provider.stream("東京")] == ["交通", "です"]
    asyncio.run(scenario())
    body = json.loads(requests[0].content)
    assert str(requests[0].url) == "http://127.0.0.1:11434/api/generate"
    assert body["stream"] is True and body["think"] is False
    assert "東京" in body["prompt"]


@pytest.mark.parametrize("status,payload", [(500, "failed"), (200, '{"error":"model missing"}\n'),
    (200, '{"response":"partial","done":false}\n'), (200, 'not json\n')])
def test_ollama_failures_become_error_events(status, payload):
    async def scenario():
        provider = OllamaGenerator("local", httpx.MockTransport(lambda r: httpx.Response(status, text=payload)))
        events = []
        async def send(event): events.append(event)
        session = Session(send, provider, 0)
        await session.update("test", True)
        await session.task
        assert events[-1]["type"] == "error"
        assert not any(e["type"] == "generation_done" for e in events)
        await session.close()
    asyncio.run(scenario())


@pytest.mark.parametrize("name", ["qwen3:cloud", "http://remote/model", "org/model", ""])
def test_cloud_models_rejected(name):
    with pytest.raises(ValueError): OllamaGenerator(name)
