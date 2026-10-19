# Reaching the broker on an appliance

Three routes, in order of preference.

## 1. Build a kubeconfig from the tenant's Rancher credential (preferred)

This is the route that works for anyone with Cogniac API credentials for the
tenant, rather than only for whoever has the right file on their laptop. Prefer
it always; a hand-held kubeconfig is a portability bug, not a shortcut.

Every tenant record carries two fields:

- `edgeflow_rancher_user_token` - a Rancher API bearer token
- `edgeflow_rancher_endpoint` - the Rancher **versioned API root**, e.g.
  `https://host:5001/v3` - not the server root

Both are readable from `GET /1/tenants/current` (or `cogniac --tenant <t> tenant
get`). Note they are deliberately ungated on the tenant API, so any caller with
tenant read access can retrieve them - treat the token accordingly.

Because the endpoint is already versioned, ask it for its own `links` map rather
than appending `/v3` yourself, and derive the `/k8s/clusters/<id>` proxy URL from
the scheme and host - the k8s proxy hangs off the *server* root. Appending to the
API root yields a confusing `404 failed to find schema v3`.

Rancher proxies each appliance's Kubernetes API at
`https://<rancher>/k8s/clusters/<cluster_id>`, and the token is the bearer
credential for it. A kubeconfig is therefore just those two values in a
template:

```yaml
clusters: [{name: X, cluster: {server: "https://<rancher>/k8s/clusters/<cluster_id>"}}]
users:    [{name: X, user: {token: "<edgeflow_rancher_user_token>"}}]
```

Clusters are named `ef-<tenant_id>-<gateway_id>`, so a gateway id resolves to a
cluster id with `GET /v3/clusters?name=ef-<tenant>-<gateway>`.

`scripts/appliance-kubeconfig.py` does all of this. Rancher's
`generateKubeconfig` action also exists and works, but it is unnecessary - it
returns a kubeconfig carrying the same credential you already hold.

This is the same mechanism `edgeflow-support/app-logs.py` uses to stream
integration-app logs, and the same one the React frontend uses for its EdgeFlow
views.

### Verify exec before relying on it

**Listing pods and streaming logs does not imply you can exec.** Running
`rabbitmqctl` needs `create` on the `pods/exec` subresource, which is a distinct
Kubernetes permission; a Rancher read-only project role grants pod reads and log
streaming while denying exec. A tenant credential may therefore get you all the
way to a working `kubectl get pods` and still fail on the first sample.

Check it up front, so the failure arrives in one second rather than five minutes
into a run:

```bash
kubectl auth can-i create pods/exec -n default
```

`appliance-kubeconfig.py` runs this by default and refuses to return a
kubeconfig that cannot exec.

### Measured result

On the one tenant tested (2026-09-10), the tenant token:

| capability | result |
|---|---|
| resolve `ef-<tenant>-<gateway>` to a cluster id | works |
| list pods | works (424 pods) |
| read pod logs | works |
| **exec into a pod** | **Forbidden** |

The real attempt, not just `auth can-i`, returned
`User "u-..." cannot create resource "pods/exec" in API group "" in the
namespace "default"`. The tenant token maps to a *restricted Rancher user*,
distinct from the user behind an operator's kubeconfig - which is why one execs
and the other does not.

That is one tenant, and roles may differ elsewhere, so probe rather than assume.
But plan for this route to be read-only until proven otherwise on your
deployment.

### Do not reflexively widen the role

The obvious response to a refusal is to add `pods/exec` to the tenant Rancher
role. Weigh that carefully rather than filing it as a config tweak.

`edgeflow_rancher_user_token` is deliberately ungated on the tenant API, so any
caller with tenant read access can retrieve it. Today that yields read-only
visibility plus logs. Granting it exec turns every tenant-scoped API credential
into shell access on that tenant's appliance pods, with no extra gate - a
privilege escalation opened for operational convenience.

A **separate ops Rancher credential** carrying exec, issued to the people who
need it, gives a whole team this route without changing what a tenant token can
do. That is the better answer in most cases; if the tenant role is widened
anyway, it should be a decision someone owns, not a side effect of getting a
script to run.

## 2. An operator-supplied kubeconfig

Some operators keep per-gateway kubeconfigs locally. These work, and are a
reasonable fallback when the tenant credential lacks exec, but do not build the
skill's normal path on them: they exist on one machine and nobody else can run
your procedure.

Confirm you are pointed where you think you are:

```bash
export KUBECONFIG=<path>
kubectl config current-context     # expect ef-<tenant>-<gateway>
```

Be aware that a locally held Rancher token may be far broader than the tenant
one - a `kubeconfig-u-*` token observed in practice could see the entire
appliance fleet across every tenant, with `importYaml` available on each. Handle
such files as fleet-wide credentials: keep them out of git, and prefer the
tenant-scoped route above.

## 3. Reverse SSH tunnel

For customer EdgeFlow appliances with no kubeconfig. Two steps.

**This is not read-only.** Opening a tunnel changes state on a customer
appliance. Get explicit authorization from the operator first, and never infer
it from a general instruction to investigate.

The gateway control-event API is a **closed set** of named events - reboot,
ping, upgrade, set-boot-software-version, factory-reset, flush-upload-queue,
time-bound-media-upload, trigger-camera-capture, and start_reverse_ssh_tunnel.
None of them carries a shell command, so there is no way to ask an appliance to
run `rabbitmqctl` directly. The tunnel is the only route.

1. `POST /1/gateways/<gw>/event/start_reverse_ssh_tunnel` with a jump-host
   address, a port, and a private key. The `edgeflow-support` repo's
   `ssh/start-ssh.py` does this; it needs the per-tenant key from the shared
   support vault.
2. The appliance dials back. SSH in over the tunnel, then use `kubectl` or
   `crictl` on the appliance itself to reach the broker pod.

Appliances poll their command queue on an interval (commonly 20 s), so expect a
short delay before the tunnel appears.

## kubectl version skew (affects every route)

Appliances often run Kubernetes v1.19-era RKE2, far behind a current client.

**Wrapper shims are the trap.** `kuberlr` (shipped by Rancher Desktop at
`~/.rd/bin/kubectl`, and usually first on `PATH`) tries to fetch a client
matching the server. For v1.19 on Apple Silicon that download 404s, because no
`darwin/arm64` build of v1.19 exists. It is worse than a clean failure: it can
fall back to a cached binary of another architecture and succeed *sometimes*,
so the error looks intermittent and environment-dependent.

Diagnose by running the real command, not `kubectl version`:

```bash
KUBECONFIG=<path> <candidate-kubectl> get pods -n default | grep rabbitmq
```

Resolve by pointing at a real binary rather than the shim. Either a cached
client matching the server version, or a current client - a modern client
normally handles `exec` against an old server despite the skew warning. Confirm
both give identical output before trusting one for a long run.

## What you cannot use

**The gateway status API.** `GET /1/gateways/<gw>/status/rabbitmq-status` looks
like the right answer and is not.

- It posts on a ~4 hour cadence, so it cannot show a burst at all.
- `queue_stats` is empty nearly always. Measured: 83 of 84 rows over 14 days on
  one appliance; 249 of 250 across five.

The producer, `edgeflow-rabbitmq-status`, is a CronJob that calls
`DELETE /api/reset` on every pass and reports only queues holding messages at
that instant. On a broker that drains normally it therefore publishes an empty
list. What it *does* carry reliably is node-level health - `mem_used`,
`fd_used`, `disk_free`, and the `mem_alarm` / `disk_free_alarm` flags - which is
worth reading when you want to know whether a deep queue is threatening the
broker's 20 GB disk floor.

## RabbitMQ management API

Reachable in-cluster on port 15672 (`/api/queues`, `/api/nodes`,
`/api/health/checks/alarms`). Equivalent to `rabbitmqctl` for depth, and easier
to parse as JSON, but it reads the stats database - which the CronJob above
wipes every few hours, punching holes in any series built from it.
`rabbitmqctl list_queues` reads live state and is unaffected, which is why the
sampling script uses it.

Never call `DELETE /api/reset` yourself.
