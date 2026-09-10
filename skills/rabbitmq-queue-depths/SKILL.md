---
name: rabbitmq-queue-depths
description: Sample and report RabbitMQ queue depths on Cogniac EdgeFlow and CloudFlow appliances, to find out whether media or app pipelines are backing up. Use this skill whenever someone asks about queue depth, queue backlog, a stuck or growing queue, whether an appliance is keeping up, why media is slow to reach CloudCore, or wants to monitor, graph, or compare broker load on one or more gateways - including when they only say "check rabbitmq on <gateway>" or "is <appliance> backed up?". Also use it before reaching for the gateway status API for queue data, because that API cannot answer the question.
---

# RabbitMQ queue depths on EdgeFlow / CloudFlow

Every EdgeFlow and CloudFlow appliance runs a RabbitMQ broker in its `default`
namespace. Application pipelines (`dsp_<app_id>`), the media upload path
(`upload`), the status forwarder (`status`), and per-API-instance queues
(`api_*`) all pass through it. Queue depth is therefore the most direct measure
of whether an appliance is keeping up with its workload.

This skill covers the whole loop: reaching the broker, sampling it safely, and
turning the samples into a report someone can act on.

## Read this first: three things that produce wrong answers

These each cost real investigation time. They are not edge cases.

**1. The gateway status API cannot answer this question.** It is the obvious
first stop and it is a dead end. `GET /1/gateways/<gw>/status/rabbitmq-status`
posts on a ~4 hour cadence, and its `queue_stats` field is empty almost always -
measured at 83 of 84 rows over 14 days on one appliance, and 249 of 250 rows
across five. The producing CronJob (`edgeflow-rabbitmq-status`) runs
`DELETE /api/reset` on every pass and reports only queues holding messages at
that instant, so a broker that is draining normally publishes nothing. Do not
build on it, and say so plainly if someone expects it to work.

**2. `consumers=0` does not mean a queue is stuck.** Appliance services use
`sqsms`, an SQS-shaped wrapper that fetches with `basic_get` polling instead of
holding a `basic_consume` subscription. Healthy, actively draining queues
therefore report zero consumers. On one fleet only 349 of 718 queues showed a
consumer at all while everything drained fine. **Depth over time is the only
reliable signal.** A queue is stuck when its depth stops falling, not when its
consumer count is zero.

**3. Never issue `DELETE :15672/api/reset`.** It blanks the broker's stats
database. Everything in this skill is read-only; keep it that way. Note that the
`edgeflow-rabbitmq-status` CronJob does this on its own schedule, which can
punch a hole in management-API-derived series (though not in `rabbitmqctl`
readings, which query live state).

## Step 1: reach the broker

Two routes. Try them in this order.

**Kubeconfig, if one exists for the appliance.** Cluster contexts are named
`ef-<tenant_id>-<gateway_id>`. Operators commonly keep per-gateway kubeconfigs
in a local directory tree; ask where, rather than guessing a path.

```bash
export KUBECONFIG=<path-to-kubeconfig>
kubectl config current-context          # expect ef-<tenant>-<gateway>
kubectl get pods -n default | grep rabbitmq
```

**Reverse SSH tunnel, when there is no kubeconfig.** This is the route for
customer EdgeFlow appliances. It is a two-step process and it is *not* read-only
- opening a tunnel changes state on a customer appliance, so get explicit
authorization first. See `references/access.md`.

### kubectl version skew will bite you

Many appliances run old Kubernetes (v1.19-era RKE2). Two failure modes:

- **Version-shim wrappers** (`kuberlr`, shipped with Rancher Desktop as
  `~/.rd/bin/kubectl`) try to download a matching client and fail when no build
  exists for the platform - there is no `darwin/arm64` build of kubectl v1.19,
  so it 404s. Worse, it *sometimes* succeeds by falling back to a cached binary,
  which makes the failure look intermittent.
- A modern client usually still works despite a large skew, because `exec` is a
  stable API.

Resolve it once, up front, by testing the actual command rather than trusting
`which kubectl`. Prefer a client matching the server version if one is cached
locally; otherwise a current client is normally fine.

## Step 2: size the window against the workload

Depth means nothing without knowing how much work went through. An appliance
sampled between jobs looks perfectly healthy. In one investigation a 20-minute
window showed a peak of 60 on an appliance that reached 626 once its real
workload arrived - the short window simply missed it.

So before sampling, establish the workload cadence and size the window to cover
several units of work. Where the deployment posts a workload-tracking status
subsystem, query it over the last 24 h and measure arrivals and duration rather
than assuming. `references/sizing.md` shows how, using the
`/1/gateways/<gw>/status/<subsystem>` endpoint.

State the sizing basis in the report. "Five hours, because each appliance sees
about one job an hour" is auditable; "five hours" is not.

## Step 3: sample

Use `scripts/sample-queues.sh`. It samples one appliance:

```bash
scripts/sample-queues.sh <gateway_id> <kubeconfig> [duration_s] [interval_s]
```

It writes `depths-<gateway_id>.tsv` as `epoch<TAB>queue<TAB>messages`, recording
only queues holding messages, plus a `__total__` and `__nqueues__` row per
sample so a fully drained sample is still evidence. Run several appliances
concurrently; each writes its own file.

Three details in that script exist for reasons worth knowing:

- **Rows are selected by "messages is numeric", not by line offset.**
  `rabbitmqctl` prints a `Timeout: 60.0 seconds ...` banner only when attached to
  a TTY. A fixed `tail -n +3` therefore drops a real queue row whenever the
  banner is absent, and inflates the queue count when it is present. This
  silently corrupted a queue count before it was caught.
- **The pod is re-resolved after repeated failures**, so a broker restart during
  a long run does not silently end the series.
- **It appends and records run markers**, so a relaunch extends a series rather
  than destroying it.

For runs longer than a session, detach with `nohup ... &` in a subshell. Note
`setsid` does not exist on macOS. Sampling every 20 s is a good default: fine
enough to catch a burst, light enough to leave the broker alone. Each call is
~1-2 s even at ~900 queues.

## Step 4: interpret before reporting

Compute these, because peak alone misleads:

- **Peak depth** - how bad it got.
- **Time above a threshold** - how long it stayed bad. These rank a fleet
  *differently*. In one run the appliance with the highest peak (6,308) spent 18
  minutes backlogged, while another peaking at only 880 spent 34 minutes. Report
  both and say they disagree; picking one silently is how a report misleads.
- **Excursions** - contiguous runs above a threshold, split where sampling shows
  a return to baseline. One 17-minute event and seventeen 1-minute events have
  the same peak and mean completely different things.
- **Ending state** - a series that ends near its peak has not drained. This is
  the single strongest "still broken" signal.

`scripts/analyze-queues.py` computes all of these and prints them.

**Distinguish a burst from a backlog.** Bursts are normal and expected during
workload; they drain within a sample or two. A backlog is a depth that stops
falling. Do not report a burst as an incident.

**Name the applications.** `dsp_<app_id>` tells a reader nothing. Resolve ids to
names with `cogniac --tenant <tenant> app get <app_id>` so the report says which
pipeline is deep. A chain of related applications backing up in sequence is a
far more useful finding than three opaque queue ids.

**Compare across appliances where you have more than one.** A queue running deep
on several appliances independently is a property of the application; deep on
one is a property of that appliance. And check the quiet end too - an appliance
doing a normal workload while queueing nothing may be misconfigured, which is
invisible if you only look for things that are too high.

## Step 5: report

`scripts/report-queues.py` renders the samples as a single self-contained HTML
page - summary tiles, a fleet comparison chart, a per-appliance breakdown, and a
cross-appliance matrix of queues that ran deep everywhere.

```bash
scripts/report-queues.py <gateway_id> [<gateway_id> ...] --out report.html
```

Lead with the verdict, not the chart. The reader wants "nothing is stuck, here
is the one thing worth chasing" in the first sentence. Derive that sentence from
the data rather than writing it by hand, so it cannot contradict the numbers
beside it.

State what you did not measure. Sampling at 20 s cannot resolve a spike lasting
15 s, and a queue that empties between samples is invisible. Say so.

## Handling customer information

Appliance investigations are customer work. Tenant ids, gateway ids, site names,
and application names are customer-identifying. Keep them out of anything
public; file evidence needing that detail against a private repo.
