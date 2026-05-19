# Cogniac CloudCore API reference

REST API reference for Cogniac CloudCore, organized one file per service. Each service's file documents every endpoint it exposes, with request/response schemas, error tables, and the auth roles required.

When you know which service handles your concern, open `<service-name>.md` directly. When you don't, scan the [Service catalog](#service-catalog) below — it lists every service with a one-line summary.

## Core concepts

CloudCore organizes computer-vision work around five entities. Most endpoints in this reference operate on one of them.

### Tenant

The top-level customer workspace. Every other entity (users, applications, subjects, media, cameras) is scoped to exactly one tenant, and all cross-tenant access is rejected by default. A user can be a member of one or more tenants; each bearer token carries a single tenant claim and authorizes the caller for that tenant only.

Managed via [tenant-core-api](tenant-core-api.md).

### Subject

A user-defined visual concept that media is associated with — for example `defective_gear`, `crack`, `good_part`, or `lobby_camera_1`. Subjects organize media for labeling and serve as the inputs and outputs of applications. A subject-media association carries a probability in `[0, 1]` and, once enough feedback accumulates, a `consensus` value of `True`, `False`, or `Sidelined`. Consensus associations are what Cogniac uses as labeled training examples.

Managed via [subject-core-api](subject-core-api.md).

### Application

The unit of computer-vision work. An application consumes media from one or more **input subjects**, runs inference through a trained model or other configured logic, and emits detections to one or more **output subjects**. Each application has an `application_type` that determines its behavior — classification, box detection, point detection, area detection, instance segmentation, OCR, network-camera capture, and others.

Managed via [application-core-api](application-core-api.md). Performance and ranking of trained models for an application is exposed by [leaderboard-service-api](leaderboard-service-api.md); evaluation metric configuration by [evaluation-metrics-api](evaluation-metrics-api.md); human-in-the-loop labeling by [feedback-service-api](feedback-service-api.md).

### Media

The images and video frames that flow through the platform. Media is uploaded directly, ingested from network cameras, or referenced in cloud storage (S3 or Azure Blob). Each media item is tenant-scoped and can be associated with subjects, queried by tag or time, and downloaded.

Managed via [media-core-api](media-core-api.md); attached short messages via [message-core-api](message-core-api.md); RTSP/MJPEG/GigE camera sources via [network-camera-core-api](network-camera-core-api.md).

### Deployment workflow

An immutable, frozen snapshot of an application's pipeline — including model, configuration, and any chained applications — pushed to an EdgeFlow appliance or CloudFlow deployment for execution. Workflows are versioned; a deployment group binds a fleet of similar EdgeFlow appliances to a specific target workflow version so the fleet runs identical inference logic.

Managed via [ef-app-provisioning](ef-app-provisioning.md) (workflow versioning), [deployment-group-core-api](deployment-group-core-api.md) (fleet binding), and [edgeflow-core-api](edgeflow-core-api.md) (appliance lifecycle).

## Authentication

All authenticated endpoints accept a Cogniac JWT in the `Authorization: Bearer <token>` header. Acquire a token by calling [token-core-api](token-core-api.md) `GET /1/token` (HTTP Basic, an API key, or an existing user token may be presented as credentials, and `tenant_id` selects which tenant to scope the issued token to). Multi-factor authentication and self-service password management are exposed by [authentication-api](authentication-api.md).

Each endpoint documents its required roles on a single line in this exact format:

```
**Auth:** Bearer JWT; required roles: `{role_a, role_b}`
```

Endpoints that accept any authenticated caller use:

```
**Auth:** Bearer JWT required
```

Endpoints that accept multiple credential forms (HTTP Basic, API key, or JWT for the caller's own account) use:

```
**Auth:** HTTP Basic, API key, or Bearer JWT for the authenticated user
```

The role set inside `{...}` is the exact set of roles that the source code admits, sorted alphabetically. Documentation across this corpus uses this format consistently — `grep -r 'roles: \`{.*\bcogniac_support\b' references/api/` returns every endpoint that admits the `cogniac_support` role, for example.

### Role taxonomy

Customer-facing roles:

| Role | Meaning |
|---|---|
| `tenant_admin` | Manages users, applications, integrations, and tenant configuration. |
| `tenant_user` | Standard tenant member; can read and operate on the tenant's data. |
| `tenant_ops` | Operator role for production / line-of-business workflows. |
| `tenant_billing` | Manages subscription, license, and contract data. |
| `tenant_creator` | Permitted to create new tenants. |
| `tenant_viewer` | Read-only access to the tenant's data. |
| `app_manager` | Listed in an application's `app_managers` array; permitted to modify that application even without `tenant_admin`. |
| `annotator` / `expert_annotator` | Permitted to submit feedback (labeling decisions) on applications they are assigned to as reviewers. |
| `license_admin` | Manages camera licenses for the tenant. |
| `subscription_manager` | Manages the tenant's subscription plan. |
| `meraki_admin` | Machine-user role for Cisco Meraki integration callers. |
| `ef_device` | Machine-user role assumed by EdgeFlow appliances when calling back to the cloud. |

Cogniac-internal roles (`cogniac_admin`, `cogniac_dev`, `cogniac_support`, `ef_ops`) gate operator-only endpoints. Cogniac employees may use these via the same APIs; external callers will receive `403` (or `404` where the endpoint deliberately hides its existence) when they attempt them.

## Conventions

- **Tenant scoping.** Every authenticated endpoint reads the tenant claim from the bearer token. Resources owned by a different tenant return `404 Not Found` (not `403`), so that the existence of cross-tenant resources cannot be probed.
- **Error envelopes.** `4xx` responses carry a JSON body with a `message` field describing the failure. `422` is used by FastAPI services for request-validation errors, with details in a structured `detail` array. `5xx` responses are server errors and may not carry a structured body.
- **Pagination.** List endpoints that paginate use cursor-style pagination: the response carries `paging.next` as a fully-qualified URL pointing to the next page. Pass `limit` to bound the page size.
- **Times.** Unix epoch seconds (number) unless otherwise noted.
- **Async operations.** Endpoints that return `202 Accepted` initiate background work; the returned identifier (`*_request_id` or similar) can be polled or correlated with later events.

## Service catalog

| Service | One-liner |
|---|---|
| [app-replay-service-v2](app-replay-service-v2.md) | Re-run media back through an application's pipeline under an updated model. |
| [application-core-api](application-core-api.md) | Create, configure, retrieve, and manage applications and their model state. |
| [authentication-api](authentication-api.md) | JWT issuance, JWT introspection, and TOTP multi-factor authentication. |
| [consensus-release-core-api](consensus-release-core-api.md) | Inspect the frozen consensus releases produced for an application. |
| [deployment-group-core-api](deployment-group-core-api.md) | Manage named fleets of EdgeFlow appliances and the workflow they run. |
| [edgeflow-core-api](edgeflow-core-api.md) | Lifecycle and runtime control of EdgeFlow appliances. |
| [ef-app-provisioning](ef-app-provisioning.md) | Workflow versioning — immutable snapshots of application pipelines for EdgeFlow/CloudFlow. |
| [ef-metrics-api](ef-metrics-api.md) | Time-series metrics for EdgeFlow appliances and CloudFlow deployments. |
| [evaluation-metrics-api](evaluation-metrics-api.md) | Per-application evaluation metric configuration (F1, ROC, IoU, Dice, count-based). |
| [feedback-service-api](feedback-service-api.md) | Human-in-the-loop labeling queue for applications. |
| [integration-build-service](integration-build-service.md) | Build and manage integration containers from caller-supplied Python source. |
| [leaderboard-service-api](leaderboard-service-api.md) | Ranked leaderboard of trained candidate models per application. |
| [license-core-api](license-core-api.md) | Meraki camera licenses and per-tenant license-expiration policy. |
| [media-core-api](media-core-api.md) | Media ingestion, retrieval, and lifecycle management. |
| [media-embedding-core-api](media-embedding-core-api.md) | Image-embedding compute for the labeling pipeline. |
| [meraki-integration-core-api](meraki-integration-core-api.md) | Tenant-scoped proxy to the Cisco Meraki dashboard API. |
| [message-core-api](message-core-api.md) | Attach short text messages to media, subjects, and applications. |
| [network-camera-core-api](network-camera-core-api.md) | Register and manage RTSP / MJPEG / GigE network cameras. |
| [ops-review-core-api](ops-review-core-api.md) | Operator-review queue for verifying or overriding application predictions. |
| [public-api](public-api.md) | Lightweight platform version probes for deployment and connectivity checks. |
| [realm-saml2-core-api](realm-saml2-core-api.md) | SAML 2.0 single sign-on and single logout for authentication realms. |
| [subject-core-api](subject-core-api.md) | Manage subjects and the subject-media association layer. |
| [tenant-core-api](tenant-core-api.md) | Manage tenants, tenant users, and tenant-level configuration. |
| [tenant-usage-core-api](tenant-usage-core-api.md) | Per-tenant resource-usage reporting. |
| [ticket-core-api](ticket-core-api.md) | Submit Cogniac support tickets from inside a customer UI. |
| [token-core-api](token-core-api.md) | Issue JWT bearer tokens used to authenticate every other API call. |
| [user-core-api](user-core-api.md) | User accounts, API keys, password resets, and tenant invitations. |
