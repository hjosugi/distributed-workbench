# 24. Containers

[All 53 topics](../ROADMAP.md) · 5. Platform knowledge · **Dockerfile and Compose**

## Meaning and purpose

A container packages an application process with its filesystem and runtime dependencies. It shares the host kernel and is not a full virtual machine. Images make distribution more repeatable, while volumes preserve selected state across container replacement.

## How the example works

The Dockerfile copies only the Python package, creates a non-root user, and stores the database under a mounted /data volume. Compose connects orders, catalog, and gateway on an internal network. Only intended local ports bind to 127.0.0.1.

Implementation: [Dockerfile](../../Dockerfile), [compose.yaml](../../compose.yaml), [.dockerignore](../../.dockerignore).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
docker compose up --build -d
```

Expected result: Orders is reachable on 8080 and the gateway on 8088. Recreating the orders container keeps its named volume, while deleting the volume removes the database.

## Tradeoffs and failure cases

Tags can change; pin image digests for stricter reproducibility. A container image does not solve dependency vulnerabilities, database migration, or backups. The local HTTP server is educational.

## Practice and interview discussion

Change the image while preserving the data volume and verify existing orders. Explain image, container, network, and volume. Interview phrase: I separate immutable application code from persistent data.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://docs.docker.com/compose/intro/compose-application-model/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
