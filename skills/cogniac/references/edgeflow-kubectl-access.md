# Read-Only kubectl Access to EdgeFlow / CloudFlow Clusters

Cogniac manages downstream EdgeFlow and CloudFlow clusters via a Rancher
control plane. Each Cogniac tenant has a per-tenant Rancher API token
(read-only, project-scoped) stored on the tenant object and reachable through
the Cogniac Python SDK. The token is the credential; `kubectl` talks to the
Rancher cluster proxy at `https://api.cogniac.io:5001/k8s/clusters/<id>`, and
Rancher enforces RBAC.

This applies equally to EdgeFlow (on-prem appliance) and CloudFlow (the
cloud-hosted equivalent) — both surface as Rancher-managed clusters reachable
the same way.

## What this gives you

A kubeconfig whose API server is the Rancher cluster proxy. All `kubectl`
traffic is brokered by Rancher and is **read-only**, enforced by the Rancher
proxy.

**Everything on an EdgeFlow/CloudFlow cluster lives in the `default`
namespace.** Always pass `-n default`.

### Works

- `kubectl get|describe nodes`
- `kubectl get|describe pods|deployments|statefulsets|daemonsets|services|ingresses|jobs|cronjobs|replicasets -n default`
- `kubectl logs <pod> [-c container] [--previous] [--since=...] [--tail=N] -n default`
- `kubectl get events --sort-by='.lastTimestamp' -n default`
- `kubectl get configmaps|pvc|endpoints -n default`

### 403s (by design)

- Cluster-scope listings other than nodes (namespaces, PVs, etc.)
- `kubectl top nodes` — `nodes.metrics.k8s.io` is not granted at cluster scope
- `kubectl exec` — no `pods/exec` verb
- `kubectl port-forward` — no `pods/portforward` verb
- `kubectl get|describe secrets`
- Anything mutating: `apply`, `create`, `delete`, `patch`, `edit`, `scale`,
  `rollout`, `cordon`, `drain`, `label`, `annotate`

## Pod naming

Once you can `kubectl get pods`, the names tell you what's running:

- `app-<application_id>-N` — StatefulSet replica `N` for application
  `<application_id>` (the 8-char Cogniac app ID). One StatefulSet per app in
  the deployed workflow, typically 8 replicas.
- `http-input-<application_id>-...` — Deployment pods for an `http_input` app.
- Everything else (`rabbitmq`, `localapi`, `uploader`, `media-storage`,
  `post-url`, `nginx-ingress-controller`, `dcgm-exporter`,
  `k8s-host-device-plugin-daemonset`, `gigev-autodiscovery`) is EdgeFlow
  infrastructure, the same on every device.

To resolve a pod back to a human-readable app name:

```bash
cogniac apps get <application_id> | jq '{application_id, name, type}'
```

The deployed workflow itself is on the EdgeFlow record:

```bash
cogniac edgeflows get <gateway_id> | jq '.deployment_group_id'
cogniac deployments list | jq '.[] | select(.deployment_group_id=="<id>") | .target_workflow_id'
cogniac workflows get <workflow_id> | jq '.app_specs[].application_id'
```

## Prerequisites

```bash
which kubectl                       # or kuberlr wrapper from Rancher Desktop
python3 -c "import cogniac"         # if missing: pip install cogniac
python3 -c "import requests"
```

Cogniac SDK credentials in the environment (usually preset by user):

```bash
export COG_API_KEY=...
cogniac auth                        # verify
```

You'll also need the **tenant_id** that owns the target gateway, passed
directly to `CogniacConnection` below — no `COG_TENANT` env var required.

## Minimum recipe (Python, ~8 lines)

The Cogniac SDK exposes two tenant fields:

- `cc.tenant.edgeflow_rancher_user_token` — bearer credential
- `cc.tenant.edgeflow_rancher_endpoint` — Rancher base URL (ends in `/v3`)

The Rancher v3 API takes two HTTP calls: resolve cluster name → id, then POST
the `generateKubeconfig` action.

```python
import requests
from cogniac import CogniacConnection

cc = CogniacConnection(tenant_id="<tenant_id>")   # or omit and set COG_TENANT in env
gw = "<gateway_id>"
cluster_name = f"ef-{cc.tenant_id}-{gw}".lower()

h = {"Authorization": f"Bearer {cc.tenant.edgeflow_rancher_user_token}"}
base = cc.tenant.edgeflow_rancher_endpoint.rstrip("/")

cid  = requests.get(f"{base}/clusters", params={"name": cluster_name}, headers=h).json()["data"][0]["id"]
yaml = requests.post(f"{base}/clusters/{cid}", params={"action": "generateKubeconfig"}, headers=h).json()["config"]

open(f"{cluster_name}.yaml", "w").write(yaml)
```

That's the whole thing. The resulting kubeconfig points at
`https://api.cogniac.io:5001/k8s/clusters/<id>` and works with stock `kubectl`.

## Gotchas

- **Token rotates.** The per-tenant Rancher token is rotated regularly on the
  Cogniac side. Fetch fresh per session rather than caching for days.
- **Cross-tenant.** One kubeconfig per tenant; pass a different `tenant_id=`
  and re-fetch.

## Quick checklist for an agent

```text
[ ] cogniac SDK installed, COG_API_KEY set
[ ] cogniac auth succeeds
[ ] Have a tenant_id and a gateway_id (tenant must own the gateway)
[ ] Run the 8-line recipe; capture the kubeconfig path in $KCFG
[ ] kubectl --kubeconfig=$KCFG -n default get pods   # smoke test; app-<id>-N pods map to Cogniac application_ids
[ ] Proceed with read-only investigation, always passing -n default
```
