# 04. JavaScript / Node.js

[All 53 topics](../ROADMAP.md) · 1. Programming languages · **Executable HTTP service**

## Meaning and purpose

JavaScript on Node.js uses an event loop for asynchronous work. A callback can serve many waiting network requests efficiently, but a long synchronous CPU task blocks other callbacks on that loop. Async code still needs explicit failure handling.

## How the example works

The example uses node:http and node:test, with no npm dependencies. createCatalog returns an unbound server so tests select an available local port. Tests use fetch against the running server, verify JSON and error status, then close the server. The direct-run entry uses Node 24.

Implementation: [examples/catalog/javascript/catalog.mjs](../../examples/catalog/javascript/catalog.mjs), [examples/catalog/javascript/catalog.test.mjs](../../examples/catalog/javascript/catalog.test.mjs).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
node --test examples/catalog/javascript/catalog.test.mjs
```

Expected result: The catalog contract test passes. Running node examples/catalog/javascript/catalog.mjs starts port 8081. The Docker composition uses this implementation as a separate catalog process.

## Tradeoffs and failure cases

Awaiting an I/O operation does not create CPU parallelism. Worker threads or separate processes may help CPU-heavy work. Shared mutable data can still race across asynchronous steps even in one event loop.

## Practice and interview discussion

Add a slow asynchronous catalog lookup, then replace it with a blocking busy loop and compare unrelated request latency. Interview phrase: Async I/O improves concurrency, but CPU work still blocks the event loop.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://nodejs.org/api/http.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
