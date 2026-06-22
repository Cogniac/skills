---
name: cogniac
description: Query and manage the Cogniac computer vision platform. Use when working with Cogniac tenants, applications, subjects, media, EdgeFlow/CloudFlow appliances, cameras, deployments, or workflows — including uploading media, checking fleet status, reading aggregate stats, or monitoring EdgeFlow/CloudFlow clusters. Triggers on references to Cogniac, CloudCore, EdgeFlow, CloudFlow, visual apps, or cogniac cli/sdk.
---

# Cogniac SDK & CLI

## Overview

Interact with the Cogniac enterprise AI computer vision platform.

**Pick the right interface:**
1. **`cogniac` CLI** — JSON output, designed for agent consumption. Use for any task it covers.
2. **`cogniac` Python SDK** — for anything the CLI doesn't expose. See `references/python-sdk.md`.

## Key Concepts

- **Tenant** — an organization/account. Users may belong to multiple tenants.
- **Application** — an ML pipeline consuming input subjects and producing output subjects. Types: `classification`, `box_detection`, `point_detection`, `point_count_detection`, `integration`, `http_input`, `camera_capture`.
- **Subject** — a category or concept (e.g., "defect", "good part"). Media flows through the system via subject associations.
- **Media** — an image or video with metadata, detections, and subject associations.
- **CloudCore** — Cogniac's cloud SaaS platform: the API, web app, and core backend services that EdgeFlow and CloudFlow connect back to. Hosted at `api.cogniac.io`.
- **EdgeFlow** — an on-premise GPU appliance running inference. Hardware models include `RM-ML80` and `IPC-M20`.
- **CloudFlow** — the cloud-hosted equivalent of EdgeFlow: same inference system, runs in CloudCore (server-side rather than on an EdgeFlow device).
- **Deployment Group** — a logical grouping of EdgeFlows for coordinated model rollout. A workflow is considered **deployed** if its ID appears as the `target_workflow_id` in any deployment group.
- **Network camera** — considered **in use** when an app of type `camera_capture` references its `network_camera_id` in `app_type_config.camera_group_list`.
- **Detection** — a model prediction or human judgment linking media to a subject with a probability (0-1).
- **Consensus** — the agreed label for a media-subject association: `True`, `False`, `Sidelined`, or `None` (undecided).
- **Feedback** — user-supplied corrections used to retrain models.

## Setup

The `cogniac` CLI ships in the `cogniac` PyPI package (requires Python >= 3.11). Use **>= 3.1.0**. Check with `cogniac --version`. If the command is missing or older, install or upgrade:

```bash
pip install 'cogniac>=3.1.0'
```

### Authentication

In the common case credentials are already in place, so `cogniac auth` is all you need — it validates the stored credential and confirms you're ready to go. Only if that fails do you need to log in:

```bash
cogniac auth              # validate credentials
cogniac auth login        # only if `cogniac auth` fails: opens the browser, authenticates
                          # via your existing Cogniac web session (password or SAML SSO),
                          # and stores a per-user API key for subsequent use
```

After one browser round-trip the credential is stored and picked up automatically by the CLI and SDK on every subsequent run — no manual key handling.

Tenant selection: most commands also need a tenant. Set `COG_TENANT`, or pass the top-level `--tenant <tenant_id>` flag, which overrides `COG_TENANT` for a single invocation (handy when switching tenants without re-exporting env vars): `cogniac --tenant <tenant_id> apps list`. `cogniac tenants` and `cogniac auth` are the exceptions — they don't need a tenant.

> Credential precedence (highest-to-lowest — the CLI/SDK uses the first it finds): explicit args → `COG_API_KEY` → stored login from `cogniac auth login`. So an exported `COG_API_KEY` takes priority over a stored login if both are present.

### First steps for any task

1. **Verify credentials:** `cogniac auth`. If it errors, run `cogniac auth login` and try again.
2. **Resolve the tenant** if `COG_TENANT` is not set or the user didn't name one. List with `cogniac tenants` and ask which to use; filter by keyword with jq:
   ```bash
   cogniac tenants | jq '.tenants[] | select(.name | test("keyword"; "i")) | {tenant_id, name}'
   ```
   Then either `export COG_TENANT=<tenant_id>` for the rest of the session, or pass `--tenant <tenant_id>` on each invocation.
3. **Run the task** using the command reference below.

## CLI Command Reference

All commands output JSON. Pipe into `jq` to filter, project, or aggregate.

### Auth & Tenants

```bash
cogniac auth login                              # browser login (preferred); stores a per-user API key
cogniac auth                                    # validate credentials, show tenant count
cogniac tenants                                 # list all authorized tenants (no COG_TENANT needed)
cogniac tenant                                  # current tenant info
```

### Applications

```bash
cogniac apps list                               # list all apps in tenant
cogniac apps get <application_id>               # get app details
cogniac apps eval-metrics <application_id>      # list active evaluation-metric configs (point_count_F1, etc.) with detection thresholds, subject weights, primary/active flags
cogniac apps leaderboard <application_id>       # ranked candidate-model snapshot. Flags: --set-assignment {validation,training}, --snapshot-type {regular,int8}, --eval-metrics {primary,all}, --top N, --full
```

### Subjects

```bash
cogniac subjects list                           # list all subjects
cogniac subjects get <subject_uid>              # get subject details
cogniac subjects search --name "exact name"     # exact name match
cogniac subjects media <subject_uid>            # list media associations
cogniac subjects media <subject_uid> --limit 10 --consensus True
cogniac subjects create "My Subject" --description "desc"
cogniac subjects associate <subject_uid> <media_id> --consensus True
```

### Media

```bash
cogniac media get <media_id>                    # get media metadata
cogniac media download <media_id>               # download to <media_id>.<ext>
cogniac media download <media_id> -o out.jpg    # download to specific path
cogniac media search --filename "img.jpg"       # search by original filename
cogniac media search --external-media-id "EXT-001"  # search by customer-supplied external ID
cogniac media search --domain-unit "SN-123"     # search by domain unit (e.g. serial number / part ID the customer groups media under)
cogniac media upload /path/to/image.jpg         # upload media
cogniac media upload /path/to/image.jpg --subject-uid <subject_uid>  # upload and associate
```

`external_media_id` and `domain_unit` are customer-set fields on the media record. Use them when the user references their own identifier (e.g. a serial number, ticket ID) rather than a Cogniac `media_id`.

### EdgeFlows

```bash
cogniac edgeflows list                          # list all EdgeFlow devices
cogniac edgeflows get <gateway_id>              # get device details
cogniac edgeflows status <gateway_id>           # recent status events (all subsystems)
cogniac edgeflows status <gateway_id> --subsystem gpus --limit 1            # latest GPU sample
cogniac edgeflows status <gateway_id> --list-subsystems                     # distinct subsystems a device reports
cogniac edgeflows status <gateway_id> --subsystem http-input-<app_id> --start <ts> --end <ts>   # time-range slice
cogniac edgeflows metrics names                                            # catalog of host/runtime metric names
cogniac edgeflows metrics list --metric-name <name> [--edgeflow-id <gateway_id>] [--start <ts> --end <ts>]
```

`--subsystem` is an exact-match filter. Built-in subsystems include `gpus`, `upload`, per-deployed-model detection counters named `model_detections_<model_instance_id>` (one per model), and `http-input-<application_id>` (one per deployed `http_input` app — see below).

**To discover what a device reports, use `--list-subsystems`** (requires `cogniac >= 3.2.0`): it returns `{subsystem, count, last_seen}` for each distinct subsystem regardless of sample frequency, then query a specific one — e.g. `--subsystem model_detections_<model_instance_id> --limit 5`. Don't page through unfiltered `status` for discovery: on a busy device the default page is entirely high-frequency `model_detections_*`, so low-frequency subsystems (`http-input-*`, `gpus`, `cpu`, `memory`) never appear. `--list-subsystems` scans up to `--scan-limit` records (default 8000); if it hits the cap it writes a `{"scan_capped": true}` notice to **stderr** (stdout stays pure JSON) — raise `--scan-limit` to widen the window.

Use `--start`/`--end` (epoch seconds or ISO 8601; requires `cogniac >= 3.2.0`) to slice a time window instead of paging `--limit`. They filter on the cloud-receipt clock (`cc_timestamp`), not device time — the two can diverge on a skewed or backfilling device.

The `http-input-<application_id>` subsystem carries ingest-side request counts. Its samples have a `status.counters` array of `{path, method, status, count}` entries, where `count` is *cumulative*; differencing the `status == "200"` / `method == "POST"` counts between two samples and dividing by elapsed time gives the ingest request rate (req/s) — the offered load on that input, distinct from model latency. Two things make this the right tool for throughput trends: EdgeFlow status is retained far longer than container logs (days), so you can see a multi-day trend the cluster's rolling logs can't; and the same payload also holds an `http_request_duration_seconds` histogram (whole-request HTTP time, not model inference).

**Computing ingest rate (req/s).** Pull a window with `--start/--end`, then difference the cumulative `POST`/`200` `/process` counts between the first and last sample and divide by elapsed time:
```bash
cogniac edgeflows status <gateway_id> --subsystem http-input-<app_id> --start <ts> --end <ts> \
  | jq '[.[] | {t: .gw_timestamp,
                c: (.status.counters[] | select(.method=="POST" and .status=="200" and (.path|test("/process"))) | .count)}]
        | (max_by(.c).c - min_by(.c).c) / ((max_by(.t).t) - (min_by(.t).t))'
```
**Multi-replica correctness.** When an `http_input` app runs more than one replica, the cumulative counter jumps or regresses as the agent samples different pods. **Track the per-endpoint cumulative max (upper envelope); never sum positive consecutive deltas** — naive delta-summing overcounts by ~20×. The first→last `max − min` above is envelope-safe.

**Timestamp schema.** Each status record carries up to three clocks: `gw_timestamp` (gateway sample clock, always present — the correct denominator for rate math), `cc_timestamp` (cloud-receipt clock, always present — what `--start/--end` filter on), and `timestamp` (guaranteed present in `cogniac >= 3.2.0`, aliased to `gw_timestamp` when the backend omits it). Sort/diff on `gw_timestamp`; on older builds ~15% of records lack `timestamp`, so `sort(key=lambda s: s["timestamp"])` `KeyError`s partway through a window.

**Counter conventions differ by subsystem** — mixing them silently corrupts results:

| Subsystem | Counter convention |
|---|---|
| `http-input-<app_id>` | **cumulative** request counts — difference between samples; use the envelope for multi-replica apps |
| `model_detections_<id>` | **per-window** counts (`window_start`/`window_end`) — don't difference across windows |

For host/runtime telemetry (cpu/disk/connectivity — hundreds of metric names) use the **`edgeflows metrics`** family (requires `cogniac >= 3.2.0`) rather than hand-differencing status counters: `metrics names` lists the available names; `metrics list --metric-name <name>` returns Grafana-shaped `[timestamp_seconds, value]` series, tenant-wide or scoped to one device with `--edgeflow-id`. `--start/--end` are optional but must be supplied together (epoch seconds or ISO 8601).

For deeper debugging beyond `cogniac edgeflows status` — pod logs, events, deployment state on the cluster itself — fetch a read-only kubeconfig via the SDK + Rancher and drive `kubectl` directly. Works for both EdgeFlow and CloudFlow clusters. See `references/edgeflow-kubectl-access.md`.

### Cameras

```bash
cogniac cameras list                            # list all network cameras
cogniac cameras get <network_camera_id>         # get camera details

# All camera IDs referenced by camera_capture apps (i.e. cameras in use)
cogniac apps list | jq '[.[] | select(.type == "camera_capture") | .app_type_config.camera_group_list[]?] | unique'

# Count cameras in use
cogniac apps list | jq '[.[] | select(.type == "camera_capture") | .app_type_config.camera_group_list[]?] | unique | length'
```

### Deployments & Workflows

```bash
cogniac deployments list                        # list all deployment groups
cogniac deployments get <deployment_group_id>   # get specific deployment group
cogniac workflows get <workflow_id>              # get workflow details
```

### System

```bash
cogniac version                                 # API version info
```

## Common Agent Workflows

### Find apps using a specific subject
Substitute the real subject UID for `s1a2b3c4d5`:
```bash
cogniac apps list | jq --arg s "s1a2b3c4d5" '[.[] | select(.input_subjects[]? == $s or .output_subjects[]? == $s) | {application_id, name, type}]'
```

### Check EdgeFlow fleet health
```bash
cogniac edgeflows list                                            # inspect JSON to pick the fields you need
cogniac edgeflows status <gateway_id> --subsystem gpus --limit 1  # latest GPU sample for one device
```

### Trace media through the pipeline
```bash
cogniac media search --domain-unit "SERIAL-001" | jq '.[0].media_id'
cogniac media get <media_id> | jq '{media_id, filename, status}'
```

### List deployed workflows
```bash
cogniac deployments list | jq -r '[.[].target_workflow_id // empty] | unique | .[]' | while read wid; do cogniac workflows get "$wid"; done
```

## Python SDK

For anything the CLI doesn't cover, use the Python SDK. The full reference is in `references/python-sdk.md`.

## Other CLIs shipped with the `cogniac` package

The `cogniac` PyPI package installs additional command-line utilities alongside the `cogniac` CLI:

### Bulk upload (`cogupload`)

For uploading many files in parallel to an input subject:

```bash
cogupload <subject_uid> <directory_name>
```

`cogupload` uses sensible defaults for parallelism and retry. It does not set the `consensus` flag, so it is suitable for ingesting raw input data for training or inference, not for labeling correction.

### Aggregate stats (`cogstats`)

```bash
cogstats -t "$COG_TENANT" [-g <gateway_id>] [-s <start_ts>] [-e <end_ts>]
```

Reports pixel counts processed and detections emitted in the time window. Default window is the last five minutes. Note: `cogstats` requires the tenant as a `-t` flag — it does not read `COG_TENANT` from the environment automatically. As of `cogniac >= 3.2.0` it sums across all per-model `model_detections_<id>` subsystems, so it reports correct totals for CloudFlow and per-model devices; earlier versions returned `0 detections / 0 pixels` for these even while they were actively processing.

## Common pitfalls

- **Multi-tenant accounts**: omitting `COG_TENANT` (or `tenant_id=` in the SDK) on a user authorized for more than one tenant causes `CogniacConnection()` to raise `ClientError(400): Unauthorized` at construction. Always set it explicitly — via `COG_TENANT`, the CLI's `--tenant` flag, or `tenant_id=` to the SDK. (The CLI's `cogniac auth` and `cogniac tenants` are the exceptions — they don't need a tenant.)
- **Authentication**: prefer `cogniac auth login` (stored credential). If you also export `COG_API_KEY`, note it takes precedence over the stored login.
- **Rate limits**: the public API enforces rate limits. Handle `429` responses with backoff; the SDK does not retry rate-limited calls automatically.
- **Region / URL prefix**: the default `https://api.cogniac.io` points at Cogniac CloudCore. Override `COG_URL_PREFIX` (or pass `url_prefix=` to `CogniacConnection`) when targeting a different deployment. Either `https://host` or `https://host/` is accepted — the SDK strips trailing slashes and any `/<version>` suffix on load.
- **Subjects vs. applications**: subjects describe *what* you care about; applications describe *how* media flows between subjects. Don't conflate them.
- **Uploads are large**: prefer `cogupload` for bulk ingestion over a custom loop; it handles parallelism and retries.

## References

- REST API reference: `references/api/README.md` — service catalog, core concepts, and per-service endpoint documentation.
- Python SDK reference: `references/python-sdk.md`.
- User guide: `references/user-guide/INDEX.md` — tutorial- and concept-oriented docs (app types, deployments, best practices, FAQ).
- Read-only kubectl access to EdgeFlow/CloudFlow clusters: `references/edgeflow-kubectl-access.md`.
- Python SDK source: https://github.com/Cogniac/cogniac-sdk-py
- PyPI package: https://pypi.org/project/cogniac/

## Feedback

This skill is meant to make Cogniac easy to drive from an agent. If anything got in your way — a command that didn't behave as documented, a field that wasn't explained, a workflow you couldn't accomplish from what's here, or guidance you wish existed — please open an issue at https://github.com/Cogniac/skills with a short note on what you were trying to do and where the skill fell short.
