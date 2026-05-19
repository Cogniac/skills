# ef-app-provisioning

Manages **workflows**: immutable, versioned snapshots of an application
pipeline (apps, subject bindings, camera bindings, tenant configuration)
ready to be deployed to an EdgeFlow appliance or to CloudFlow.

A workflow has two parts:

- A **workflow base** identified by `base_id`. The base is mutable
  pipeline-level metadata (name, description, target EdgeFlow model,
  auto-version policy) plus a pointer to the latest version.
- A sequence of **workflow versions** under that base, each identified
  by `workflow_id` of the form `<base_id>:<version>` where `version`
  starts at `0` and increments by `1`. Versions themselves are
  immutable: changing the pipeline produces a new version, never an
  in-place edit.

The typical customer lifecycle:

1. `POST /1/workflows` to create the initial base and version `0`.
2. `POST /1/workflows/{base_id}/versions` to produce subsequent
   versions as the pipeline evolves.
3. `GET /1/workflows/{base_id}/versions` and
   `GET /1/workflows/{workflow_id}` to inspect history and the rendered
   deployment.
4. `PATCH /1/workflows/{workflow_id}` to adjust workflow-base policy
   (e.g. auto-versioning).
5. Reference the workflow from a Deployment Group to push it to
   EdgeFlow / CloudFlow.

Workflow versions cannot be deleted while a Deployment Group still
references them.

## Endpoints

### `GET /1/workflows/version`

Return the running service version string.

**Auth:** no auth required

**Responses:**

| Status | Description |
|---|---|
| 200 | `{ "api_version": "1", "build": "<build-id>" }` |

### `POST /1/workflows`

Create a workflow base and its initial version (`version = 0`).

The request body carries the pipeline definition (`app_specs`),
tenant-level subject / camera / custom configuration, and the target
`edgeflow_model`. On success the service:

- assigns a `base_id`,
- renders the deployment artifact for the chosen `edgeflow_model`,
- stores the rendered artifact and the supplied tenant configs as the
  workflow's immutable assets,
- writes the workflow base and version `0`,
- returns the new version record (including `workflow_id`,
  `_apply_jsons`, and the echoed `app_specs`).

The total number of entries in `app_specs` must not exceed the pod
capacity of the chosen `edgeflow_model`
(see `GET /1/workflows/eftargets/{edgeflow_model}`).

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_user}`

**Request body** (`application/json`):
[CreateWorkFlowRequestSchema](#schema-createworkflowrequestschema).

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Created workflow version (includes `_apply_jsons` and `app_specs`). | [WorkFlowSchema](#schema-workflowschema) |

**Errors:**

- `400` — empty body, validation failure, unsupported `edgeflow_model`,
  or `app_specs` size exceeds the model's pod capacity.
- `401` — missing or invalid bearer token.
- `500` — failed to persist workflow assets.

### `POST /1/workflows/{base_id}/versions`

Create a new version under an existing workflow base.

The base's `edgeflow_model` is fixed at base-creation time. If the
request supplies `edgeflow_model` it must match the base's value;
mismatches are rejected. Fields omitted from the request body (notably
`name` and `description`) are inherited from the previous version.

The new `version` is one greater than the current latest version. The
base's `latest_version`, `latest_workflow_id`, `name`, `description`,
`updated_by`, and `updated_at` are updated to point at the new version.

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_user}`

**Path params:**

| Name | Type | Description |
|---|---|---|
| `base_id` | string | Workflow base identifier. |

**Request body** (`application/json`):
[CreateWorkFlowVersionRequestSchema](#schema-createworkflowversionrequestschema).

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Created workflow version (includes `_apply_jsons` and `app_specs`). | [WorkFlowSchema](#schema-workflowschema) |

**Errors:**

- `400` — empty body, validation failure, `base_id` not found,
  `edgeflow_model` mismatch with the base, or `app_specs` size exceeds
  the model's pod capacity.
- `401` — missing or invalid bearer token.
- `500` — failed to persist workflow assets.

### `GET /1/workflows/{base_id}/versions`

List all versions of a workflow base, newest first by default.

The response is a paginated summary list. The bulky deployment artifact
(`_apply_jsons`) and `app_specs` are **omitted** from the list view;
fetch a specific version via `GET /1/workflows/{workflow_id}` to see
them.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `base_id` | string | Workflow base identifier. |

**Query params** (`WorkFlowVersionQuerySchema`):

| Name | Type | Description |
|---|---|---|
| `reverse` | boolean | Newest-first when true (default). |
| `limit` | integer | Max items per page (default 100). |
| `last_key` | string | Pagination cursor returned by a previous call. |

**Responses:**

| Status | Description |
|---|---|
| 200 | `{ "data": [WorkFlowSchema, ...], "last_key": <cursor or null> }` |

**Errors:**

- `401` — missing or invalid bearer token.

### `GET /1/workflows/{base_id}/versions/{version}`

Get a specific workflow version.

Returns the full version record including the rendered deployment
artifact (`_apply_jsons`), the `app_specs`, and the tenant
configuration snapshots that were captured when the version was
created. The response also includes
`system_software_updates_available` — a boolean flag indicating
whether re-rendering the version with the current platform image
catalog would produce different non-tenant-specific images (i.e.
whether an update is available without changing the pipeline).

For backward compatibility, `base_id` may be passed as either a bare
`base_id` or a `base_id:version` string; the latter is truncated to its
`base_id` portion.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `base_id` | string | Workflow base identifier. |
| `version` | integer | Version number (starts at 0). |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Workflow version record. | [WorkFlowSchema](#schema-workflowschema) |

**Errors:**

- `401` — missing or invalid bearer token.
- `404` — version or its base not found.

### `GET /1/workflows/{workflow_id}`

Get a single workflow version by its full `workflow_id`
(`<base_id>:<version>`).

Equivalent to
`GET /1/workflows/{base_id}/versions/{version}` and returns the same
shape, including `_apply_jsons`, `app_specs`, captured tenant
configuration, and the `system_software_updates_available` flag.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `workflow_id` | string | Full workflow version identifier (`<base_id>:<version>`). |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Workflow version record. | [WorkFlowSchema](#schema-workflowschema) |

**Errors:**

- `401` — missing or invalid bearer token.
- `404` — workflow or its base not found.

### `PATCH /1/workflows/{workflow_id}`

Update mutable workflow-base policy fields.

This endpoint targets the **workflow base**, not an individual
version. The `workflow_id` path parameter accepts either a `base_id`
or a `base_id:version` string; in the latter case only the `base_id`
portion is used.

Only fields present in the request body are modified. The fields
intended for update through this endpoint are `auto_version` and
`auto_version_triggers`; any other fields submitted are subject to
[WorkFlowBaseSchema](#schema-workflowbaseschema) validation in partial
mode.

`updated_by` and `updated_at` on the base are refreshed to the caller
and the current server time.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `workflow_id` | string | Workflow base id, optionally suffixed with `:<version>` (suffix ignored). |

**Request body** (`application/json`): partial
[WorkFlowBaseSchema](#schema-workflowbaseschema).

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Updated workflow base record. | [WorkFlowBaseSchema](#schema-workflowbaseschema) |

**Errors:**

- `400` — validation failure on the partial body.
- `401` — missing or invalid bearer token.
- `404` — workflow base not found.

### `DELETE /1/workflows/{workflow_id}`

Delete a single workflow version.

Deletion is refused if any Deployment Group currently references this
`workflow_id` as its `current_workflow_id`; detach or re-point the
referring Deployment Groups before retrying.

After the version is removed, its workflow base is reconciled:

- if other versions remain, the base is updated to point at the new
  latest version (name, description, `latest_version`,
  `latest_workflow_id`, `updated_by`, `updated_at`),
- if no versions remain, the workflow base itself is deleted.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `workflow_id` | string | Full workflow version identifier (`<base_id>:<version>`). |

**Responses:**

| Status | Description |
|---|---|
| 204 | Deleted; no body. |

**Errors:**

- `400` — workflow version is still referenced by one or more
  Deployment Groups (the response message names them).
- `401` — missing or invalid bearer token.
- `404` — workflow version not found.

### `GET /1/workflows/eftargets`

List the EdgeFlow model identifiers supported as workflow deployment
targets.

**Auth:** Bearer JWT required

**Responses:**

| Status | Description |
|---|---|
| 200 | Array of supported `edgeflow_model` strings. |

### `GET /1/workflows/eftargets/{edgeflow_model}`

Get the capability descriptor for a single EdgeFlow model.

The descriptor reports the model's pod capacity, GPU configuration,
total GPU memory, and related target attributes. Use the pod capacity
to validate that an intended `app_specs` list will fit on the chosen
model before calling `POST /1/workflows`.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `edgeflow_model` | string | EdgeFlow model identifier from `GET /1/workflows/eftargets`. |

**Responses:**

| Status | Description |
|---|---|
| 200 | EdgeFlow model capability descriptor. |

## Schemas

### `AppSpecSchema` <a id='schema-appspecschema'></a>

Per-application entry inside a workflow's `app_specs` array. One entry
describes one application slot in the pipeline.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `application_id` | string | no | default=None | Identifier of the source application this slot is derived from. |
| `model_runtime_image` | string | no | default=None | Container image to use as the model runtime for this app. |
| `input_subject_uids` | list[any] \| null | no |  | Subjects that feed this app's input. |
| `gpu_policy` | any | no | default=None | This field contains the complete GPU-related policy configuration for an application, and is expected to contain nested objects as needed. |

### `WorkFlowBaseSchema` <a id='schema-workflowbaseschema'></a>

Workflow base record: pipeline-level metadata and a pointer to the
latest version.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `tenant_id` | string | **yes** |  | Owning tenant. |
| `workflow_id` | string | **yes** |  | Workflow base identifier. Serialized as `base_id` on the wire. |
| `name` | string | **yes** |  | name and description mirror those of the latest workflow version |
| `description` | string \| null | no | default=None | Free-form description; mirrors the latest version's description. |
| `latest_version` | integer | **yes** |  | Version number of the most recent workflow version under this base. |
| `latest_workflow_id` | string | **yes** |  | `workflow_id` (`<base_id>:<version>`) of the most recent version. |
| `edgeflow_model` | string | **yes** |  | Target EdgeFlow model. Fixed at base-creation time and shared by every version. |
| `created_by` | string | **yes** |  | Email of the user that created the base. |
| `created_at` | number | **yes** |  | Base creation timestamp (seconds since the epoch). |
| `updated_by` | string | **yes** |  | these two fields equal created_by and created_at fields in the latest workflow version |
| `updated_at` | number | **yes** |  | Timestamp of the most recent version creation under this base (seconds since the epoch). |
| `auto_version` | boolean | no | default=False | When true, automatic version creation is enabled for this workflow base. |
| `auto_version_triggers` | list[string] | no |  | Subset of the auto-version trigger names that, when fired, will produce a new version while `auto_version=true`. Allowed values: `model_release`, `application_update`, `subject_update`, `camera_update`, `tenant_update`. Omitted on create defaults to all five enabled. Always an array on the wire; explicit `null` is rejected; explicit `[]` disables all triggers. |

### `CreateWorkFlowRequestSchema` <a id='schema-createworkflowrequestschema'></a>

Request body for `POST /1/workflows`.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `base_id` | string | no |  | Presence of base_id signifies the intent to create the workflow version |
| `name` | string | no |  | Human-readable workflow name. Required when creating a new base; inherited from the previous version when adding a version. |
| `description` | string \| null | no |  | Free-form description. |
| `edgeflow_model` | string | no |  | Target EdgeFlow model. Required when creating a new base; must equal the base's value when adding a version. |
| `app_specs` | any | no |  | Array of [AppSpecSchema](#schema-appspecschema) entries defining the pipeline. Size must not exceed the chosen model's pod capacity. |
| `tenant_subject_config` | any \| null | **yes** |  | Snapshot of tenant subject configuration to capture in this workflow version. |
| `tenant_camera_config` | any \| null | **yes** |  | Snapshot of tenant camera configuration to capture in this workflow version. |
| `tenant_custom_data` | any \| null | no | default=None | Snapshot of tenant custom data to capture in this workflow version. |
| `created_by` | string \| null | no | default=False | Override for the user attributed as creator. When omitted, the authenticated caller is used. |
| `auto_version` | boolean | no | default=False | Initial value of the base's `auto_version` flag. |
| `auto_version_triggers` | list[string] | no |  | Initial value of the base's `auto_version_triggers`. Allowed values: `model_release`, `application_update`, `subject_update`, `camera_update`, `tenant_update`. Omitting the field uses the default of all five triggers; explicit `[]` disables all triggers; explicit `null` is rejected. |

### `CreateWorkFlowVersionRequestSchema` <a id='schema-createworkflowversionrequestschema'></a>

Request body for `POST /1/workflows/{base_id}/versions`.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `name` | string | no |  | Workflow name for the new version. Defaults to the previous version's name. |
| `description` | string \| null | no |  | Description for the new version. Defaults to the previous version's description. |
| `edgeflow_model` | string | no |  | If supplied, must equal the workflow base's `edgeflow_model`; mismatches are rejected. |
| `app_specs` | any | no |  | Array of [AppSpecSchema](#schema-appspecschema) entries defining the pipeline. Size must not exceed the chosen model's pod capacity. |
| `tenant_subject_config` | any \| null | **yes** |  | Snapshot of tenant subject configuration to capture in this workflow version. |
| `tenant_camera_config` | any \| null | **yes** |  | Snapshot of tenant camera configuration to capture in this workflow version. |
| `tenant_custom_data` | any \| null | no | default=None | Snapshot of tenant custom data to capture in this workflow version. |
| `created_by` | string \| null | no | default=False | Override for the user attributed as creator. When omitted, the authenticated caller is used. |
| `auto_version` | boolean | no | default=False | When supplied, updates the workflow base's `auto_version` flag. |
| `auto_version_triggers` | list[string] | no |  | When supplied, updates the workflow base's `auto_version_triggers`. Allowed values: `model_release`, `application_update`, `subject_update`, `camera_update`, `tenant_update`. Always an array; explicit `null` is rejected. |

### `WorkFlowSchema` <a id='schema-workflowschema'></a>

Workflow version record returned by version-scoped reads and on create.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `tenant_id` | string | **yes** |  | Owning tenant. |
| `workflow_id` | string | no |  | Full version identifier, `<base_id>:<version>`. |
| `base_id` | string | **yes** |  | Workflow base this version belongs to. |
| `version` | integer | **yes** |  | Version number under the base (starts at 0). |
| `name` | string | **yes** |  | Workflow name at the time this version was created. |
| `description` | string \| null | no | default=None | Description at the time this version was created. |
| `edgeflow_model` | string | **yes** |  | Target EdgeFlow model; identical across all versions of a base. |
| `created_by` | string | **yes** |  | Email of the user that created this version. |
| `created_at` | number | **yes** |  | Version creation timestamp (seconds since the epoch). |
| `auto_version` | boolean | no | default=False | Current value of the workflow base's `auto_version` flag (echoed for convenience). |
| `auto_version_triggers` | list[string] | no |  | Current value of the workflow base's `auto_version_triggers` (echoed for convenience). Allowed values: `model_release`, `application_update`, `subject_update`, `camera_update`, `tenant_update`. Always an array; explicit `null` is rejected. |
| `tenant_subject_config` | any | no |  | Snapshot of tenant subject configuration captured at version creation. |
| `tenant_camera_config` | any | no |  | Snapshot of tenant camera configuration captured at version creation. |
| `tenant_custom_data` | any | no |  | Snapshot of tenant custom data captured at version creation. |

### `WorkFlowVersionQuerySchema` <a id='schema-workflowversionqueryschema'></a>

Query parameters for `GET /1/workflows/{base_id}/versions`.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `reverse` | boolean | no | default=True | When true, return newest-first. |
| `last_key` | string \| null | no |  | Pagination. |
| `limit` | integer \| null | no | default=100 | Maximum number of versions to return per page. |
