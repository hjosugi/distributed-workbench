# 41. TCP

[All 53 topics](../ROADMAP.md) · 7. Networking and security · **Real framed byte-stream exchange**

## Meaning and purpose

TCP provides a reliable ordered byte stream between endpoints. It does not preserve application message boundaries. A receive call may return only part of a message or several logical messages together.

## How the example works

The client writes one frame in several pieces. A four-byte big-endian length prefix describes the payload. recv_exact loops until the requested byte count arrives or raises EOFError on premature closure. The server validates a maximum frame size and echoes the frame.

Implementation: [architect_lab/networking.py](../../architect_lab/networking.py).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 -m architect_lab.networking
```

Expected result: The payload hello is reconstructed successfully. A separate test closes a connection in the middle of a frame and verifies that truncation is rejected.

## Tradeoffs and failure cases

Reliable transport does not mean a business action happened exactly once. An application still needs timeouts, framing limits, cancellation, and retry identity. The OS implements TCP congestion control and retransmission; this lab implements application framing.

## Practice and interview discussion

Explain why recv(1024) is not a complete-message API. Describe the ambiguity after a write followed by a connection reset. Interview phrase: TCP is a byte stream, so I define explicit message framing.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://www.rfc-editor.org/rfc/rfc9293.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
