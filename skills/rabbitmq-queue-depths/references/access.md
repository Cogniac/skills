# Reaching the broker on an appliance

Two routes, in order of preference.

## 1. Kubeconfig

CloudFlow appliances, and any EdgeFlow onboarded with one, have a kubeconfig
giving direct cluster access. Contexts are named `ef-<tenant_id>-<gateway_id>`,
which is how you confirm you are pointed at the appliance you think you are.

```bash
export KUBECONFIG=<path>
kubectl config current-context
kubectl get pods -n default | grep rabbitmq
```

Operators keep these in a local directory tree, one per gateway. Ask where
rather than guessing; the layout is a local convention, not a platform one.

### Version skew

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

## 2. Reverse SSH tunnel

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
