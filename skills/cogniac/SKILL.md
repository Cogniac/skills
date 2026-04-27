---
name: cogniac
description: Use this skill when working with the Cogniac computer vision platform —
  installing or using the `cogniac` Python SDK, the `cogniac` CLI, the legacy
  `cogupload` / `cogstats` / `icogniac` utilities, or calling the Cogniac public
  REST API directly. Activate whenever a user asks how to authenticate to Cogniac,
  create or query subjects/applications/media, ingest data, train models, deploy to
  EdgeFlow gateways, or read detection results — including from agentic / coding
  contexts.
---

# Cogniac

Cogniac is a computer vision platform: you upload media, define subjects (concepts
the system should learn), wire them through applications (workflows that classify,
detect, count, or compare), and consume the resulting detections via API or pushed
to downstream systems. This skill teaches an agent how to use Cogniac end-to-end
through the official Python SDK, the `cogniac` command-line tool, and the public
REST API.

## When to use this skill

Activate this skill when:

- The user mentions Cogniac, the `cogniac` Python package, the `cogniac` CLI,
  `cogupload`, `cogstats`, or `icogniac`.
- The user wants to authenticate to a Cogniac tenant or API endpoint.
- The user wants to create, list, update, or delete subjects, applications, media,
  tenants, gateways (EdgeFlow), deployment groups, network cameras, or feedback.
- The user wants to upload images or video for inference, retrieve detections, or
  query model results.
- The user is writing code (Python or otherwise) that calls `https://api.cogniac.io/`
  endpoints, including from inside another agent.
- The user asks how to deploy a model to an edge gateway / EdgeFlow box.

If the user is asking about Cogniac's *internal* / non-public APIs, services, or
infrastructure, this skill does not cover those — defer to internal docs.

## Quickstart: install and authenticate

The Cogniac SDK is published on PyPI as `cogniac` and supports Python 2.7 and
Python 3.

```bash
pip install cogniac
```

Set credentials via environment variables (recommended for agents):

```bash
export COG_API_KEY="your-cogniac-api-key"
export COG_TENANT="your-tenant-id"        # only required if user has multiple tenants
export COG_URL_PREFIX="https://api.cogniac.io/"  # default; override for on-prem
```

Alternatively, username + password:

```bash
export COG_USER="you@example.com"
export COG_PASS="your-password"
```

Then in Python:

```python
import cogniac

cc = cogniac.CogniacConnection()  # picks up env vars automatically
print(cc.get_tenant())
print(cc.get_all_applications())
print(cc.get_all_subjects())
```

Or pass credentials explicitly:

```python
cc = cogniac.CogniacConnection(
    api_key="your-cogniac-api-key",
    tenant_id="your-tenant-id",          # optional
    url_prefix="https://api.cogniac.io/",
    timeout=60,
)
```

If a user is a member of multiple tenants, list them with
`CogniacConnection.get_all_authorized_tenants()` and pass the chosen
`tenant_id` to a fresh `CogniacConnection`.

## Core concepts

| Concept | What it is |
|---------|------------|
| **Tenant** | The top-level account boundary. All resources belong to one tenant. |
| **Subject** | A user-defined concept — a class, object, or event the platform should track. Subjects are the central organizational unit. |
| **Application** | A workflow that consumes media from input subjects, runs inference, and emits results to output subjects. |
| **Media** | Images, videos, or frames ingested into the system. Each media item is associated with at least one subject. |
| **Gateway / EdgeFlow** | An on-premises edge device that runs Cogniac models locally. (`Gateway` is the legacy name; `EdgeFlow` is current. Same product.) |
| **Deployment Group** | A logical grouping of EdgeFlow gateways for coordinated model rollout. |
| **Detection** | An inference result tied to a media item, with bounding boxes / labels / scores. |
| **Feedback** | User-supplied corrections used to retrain models. |

## Common SDK operations

The main entry point is `cogniac.CogniacConnection`. Helper methods:

```python
# Tenants
cc.get_tenant()
cc.get_all_authorized_tenants()  # classmethod

# Subjects
cc.get_all_subjects()
cc.get_subject(subject_uid)
cc.create_subject(name="my-subject", description="...")

# Applications
cc.get_all_applications()
cc.get_application(application_id)
cc.create_application(name="my-app", application_type="...", ...)

# Media
cc.get_media(media_id)
cc.create_media(filename="path/to/image.jpg")
```

Mutable attributes on `CogniacApplication`, `CogniacSubject`, `CogniacMedia`, and
`CogniacTenant` are persisted to the API on assignment — no explicit `save()` call
needed.

### Upload media to a subject

```python
subject = cc.get_subject("my-subject-uid")
media = cc.create_media(filename="photo.jpg")
subject.associate_media(media.media_id)
```

### Bulk upload (CLI)

For uploading many files in parallel to an input subject:

```bash
cogupload <subject_uid> <directory_name>
```

`cogupload` uses sensible defaults for parallelism and retry. It does not set
the `consensus` flag, so it is suitable for ingesting raw input data for training
or inference, not for labeling correction.

### Aggregate stats (CLI)

```bash
cogstats -t <TENANT_ID> [-g GATEWAY_ID] [-s START_TS] [-e END_TS]
```

Reports pixel counts processed and detections emitted in the time window. Default
window is the last five minutes.

### Interactive REPL

```bash
icogniac [partial-tenant-name-or-id]
```

Drops the user into IPython with the `cc` connection pre-bound and helper magics
like `%media_detections <media_id>` and `%media_subjects <media_id>`.

### Top-level CLI

The `cogniac` command (installed by the same package) wraps SDK operations for
shell-friendly use. Run `cogniac --help` for the current subcommand list.

## Calling the public API directly

When the SDK isn't a fit (e.g. non-Python agents, raw HTTP calls), call the
Cogniac public API directly:

```bash
BASE="https://api.cogniac.io"   # or your on-prem URL prefix
TOKEN="..."                     # bearer token from /1/users/current/tokens

curl -H "Authorization: Bearer $TOKEN" "$BASE/1/tenants/$TENANT_ID"
curl -H "Authorization: Bearer $TOKEN" "$BASE/1/applications"
curl -H "Authorization: Bearer $TOKEN" "$BASE/1/subjects"
```

Auth flow:

1. POST credentials to `/1/users/current/tokens` to get a JWT.
2. Pass the JWT as `Authorization: Bearer <token>` on subsequent requests.
3. If acting on a multi-tenant user, include the `tenant_id` claim or call the
   `/1/tenants/<tenant_id>/...` endpoint family.

Pagination, filters, and resource-specific request/response shapes are documented
inline in the public docs (see References).

## On-prem and self-hosted Cogniac

If the user is on a private Cogniac deployment, point the SDK at it via
`url_prefix` or `COG_URL_PREFIX`:

```python
cc = cogniac.CogniacConnection(
    url_prefix="https://your-org.local.cogniac.io/",
    api_key="...",
)
```

The API surface is identical between cloud and on-prem.

## Common pitfalls

- **Multi-tenant accounts**: omitting `tenant_id` on a multi-tenant user causes
  unexpected behavior. Always set `COG_TENANT` or pass `tenant_id=` explicitly.
- **Mixing username/password and API key**: pick one. API keys are preferred for
  agents and CI.
- **Rate limits**: the public API enforces rate limits. Handle `429` responses
  with backoff; the SDK does not retry rate-limited calls automatically.
- **Region / URL prefix**: the default `https://api.cogniac.io/` is for Cogniac
  CloudCore. On-prem users **must** override it or all calls will hit cloud.
- **Subjects vs. applications**: subjects describe *what* you care about;
  applications describe *how* media flows between subjects. Don't conflate them.
- **Uploads are large**: prefer `cogupload` for bulk ingestion over a custom loop;
  it handles parallelism and retries.

## References

- Public documentation: https://docs.cogniac.io/
- Cogniac website: https://www.cogniac.io/
- Python SDK source: https://github.com/Cogniac/cogniac-sdk-py
- PyPI package: https://pypi.org/project/cogniac/
- Public API base URL (cloud): https://api.cogniac.io/
- Support: support@cogniac.co

### Public API endpoint coverage

The full public API is documented at https://docs.cogniac.io/. High-level
endpoint families an agent will commonly need:

- `/1/users/current` — current user, token issuance, authorized tenants.
- `/1/tenants/<tenant_id>` — tenant settings, members, roles.
- `/1/subjects` — subject CRUD and media associations.
- `/1/applications` — application CRUD, types, and configuration.
- `/1/media` — media upload, retrieval, deletion.
- `/1/media/<media_id>/detections` — inference results for a given media item.
- `/1/feedback` — user-supplied corrections for retraining.
- `/1/gateways` (a.k.a. EdgeFlow) — edge device registration and status.
- `/1/deploymentGroups` — model rollout groupings.
- `/1/networkCameras` — RTSP / network camera configuration.

When in doubt about request/response shape, consult the live docs or inspect
the SDK source — the SDK is a thin wrapper over these endpoints and is the
authoritative reference for their concrete shapes.
