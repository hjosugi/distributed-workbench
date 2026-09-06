"""One connection owns its transcript and cancellable generation task."""

import asyncio
import contextlib
import time


class Session:
    def __init__(self, send, generator, debounce_ms=350):
        self.send = send
        self.generator = generator
        self.debounce_ms = debounce_ms
        self.revision = 0
        self.segment = 1
        self.confirmed = ""
        self.partial = ""
        self.task = None
        self.closed = False

    async def cancel_generation(self):
        if self.task is not None:
            self.task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.task
            self.task = None

    async def update(self, text: str, is_final: bool):
        text = text.strip()
        if not is_final and text == self.partial:
            return
        if is_final and not text and not self.partial:
            return
        self.revision += 1
        await self.cancel_generation()
        current_segment = self.segment
        if is_final:
            self.confirmed = " ".join(filter(None, [self.confirmed, text]))[-2000:]
            self.partial = ""
            self.segment += 1
        else:
            self.partial = text
        transcript = " ".join(filter(None, [self.confirmed, self.partial]))[-2000:]
        await self.send({
            "type": "transcript", "revision": self.revision,
            "segment": current_segment, "text": text,
            "confirmed": self.confirmed, "partial": self.partial,
            "is_final": is_final,
        })
        if transcript:
            self.task = asyncio.create_task(
                self.generate(self.revision, transcript, is_final, time.monotonic())
            )

    async def generate(self, revision, transcript, is_final, received_at):
        try:
            if not is_final:
                await asyncio.sleep(self.debounce_ms / 1000)
            if revision != self.revision or self.closed:
                return
            await self.send({"type": "generation_start", "revision": revision})
            first = True
            count = 0
            async with asyncio.timeout(120):
                async for delta in self.generator.stream(transcript):
                    if revision != self.revision or self.closed:
                        return
                    if not isinstance(delta, str):
                        raise ValueError("Generator returned a non-text delta")
                    if not delta:
                        continue
                    count += len(delta)
                    if count > 8000:
                        raise ValueError("Generation exceeded 8000 characters")
                    await self.send({
                        "type": "generation_delta", "revision": revision, "text": delta,
                        "ttft_ms": round((time.monotonic() - received_at) * 1000) if first else None,
                    })
                    first = False
            await self.send({"type": "generation_done", "revision": revision})
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            if not self.closed and revision == self.revision:
                await self.send({
                    "type": "error", "revision": revision,
                    "message": f"生成に失敗しました: {type(exc).__name__}: {str(exc)[:240]}",
                })

    async def reset(self):
        self.revision += 1
        await self.cancel_generation()
        self.confirmed = self.partial = ""
        self.segment = 1
        await self.send({"type": "reset", "revision": self.revision})

    async def close(self):
        self.closed = True
        await self.cancel_generation()
