# 25. Orchestration / Kubernetes

[All 53 topics](../ROADMAP.md) · 5. Platform knowledge · **Deployment, Service, probes, resource limits**

## Meaning and purpose

Orchestration reconciles a desired state: how many replicas should run, how traffic reaches them, and how failures are detected. Kubernetes Deployments manage replaceable pods; Services provide stable discovery and routing.

## How the example works

The manifest uses one replica, resource requests and limits, readiness and liveness probes, a restricted container context, and a Service. The image must first be built and loaded into your local cluster. This lesson uses emptyDir for an explicitly ephemeral database.

Implementation: [infra/k8s/orders.yaml](../../infra/k8s/orders.yaml).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
kubectl apply --dry-run=client -f infra/k8s/orders.yaml
```

Expected result: With a configured cluster and loaded image, the pod becomes Ready and the Service forwards to port 8080. See the integration guide for kind and port-forward commands.

## Tradeoffs and failure cases

Pod replacement loses emptyDir data. Do not scale this SQLite deployment to multiple independent replicas and assume a shared order database. Production requires a suitable durable store, backup, migration, and failure design. Dry-run is not a running-cluster test.

## Practice and interview discussion

Delete the lab pod and observe reconciliation and data loss. Explain readiness versus liveness. Interview phrase: Kubernetes replaces processes, but application durability is still our responsibility.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
