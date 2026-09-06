# 01. Java

[All 53 topics](../ROADMAP.md) · 1. Programming languages · **Executable HTTP service**

## Meaning and purpose

Java uses static types and JVM bytecode. In an architecture discussion, focus on team experience, deployment, memory, concurrency, and library support. The same network contract can be implemented in several languages; the language does not define the service boundary.

## How the example works

The JDK HttpServer registers one handler, checks method and path, writes UTF-8 JSON, and closes the response stream. Product prices use integer yen. A source-file launch compiles and runs the example without a build tool. This example targets Java 17 or later; it does not claim Java 17 is the latest release.

Implementation: [examples/catalog/java/Catalog.java](../../examples/catalog/java/Catalog.java).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
java examples/catalog/java/Catalog.java
```

Expected result: GET /products returns book=1200 and pen=200. GET /health returns status=ok. A missing route returns 404; POST returns 405. Use scripts/check_catalogs.py java for the contract test.

## Tradeoffs and failure cases

This small server does not include production authentication, request instrumentation, or graceful shutdown. JVM tuning and virtual threads are separate decisions. A virtual thread makes blocking concurrency cheaper; it does not automatically make business operations parallel or atomic.

## Practice and interview discussion

Add a third product and keep the contract identical across all four languages. Explain why a shared JSON contract is more stable than sharing language-specific classes. Interview phrase: I choose the language based on the team and operational needs.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.oracle.com/en/java/javase/17/docs/api/jdk.httpserver/com/sun/net/httpserver/HttpServer.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
