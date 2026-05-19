# deployment-group-core-api

A deployment group is a named, tenant-scoped collection of EdgeFlow appliances that share a common deployment target — a workflow whose model and pipeline configuration should be installed on every EdgeFlow in the group. Use deployment groups to roll a single workflow out to a fleet of EdgeFlows, to schedule recurring deployments via cron expressions, or to trigger an immediate "deploy now" of a specific workflow to every EdgeFlow in the group. EdgeFlows are attached to a deployment group by setting their `deployment_group_id`; an EdgeFlow can belong to at most one deployment group at a time.

The API surfaces two related resources. `deploymentCapacityClasses` describes the EdgeFlow hardware capacity tiers (for example, a class corresponding to a specific Cogniac appliance product family); it is a read-only reference list for tenant callers and is the same across all tenants. `deploymentGroups` is the primary resource for managing a tenant's deployment groups: create and configure a group, list and inspect its member EdgeFlows, drive workflow rollouts (immediate, scheduled, or auto-update on new versions), pre-pull container images for an upcoming workflow, and read the audit history of past deployments. A tenant's contract may cap the total number of deployment groups it can hold; once a deployment group has any EdgeFlows attached, it cannot be deleted until those EdgeFlows are reassigned.

Workflow rollout in a deployment group is modelled as a small state machine across three workflow id fields. `target_workflow_id` is the workflow the group should converge to. `current_workflow_id` reports the last workflow successfully applied. `next_workflow_id` is set by callers to request a change; the scheduler — or, if no schedule is configured, an immediate deployment event triggered by the update call — advances `target_workflow_id`, and `current_workflow_id` is updated as EdgeFlows report success. Separately, `deploy_now_workflow_id` triggers a one-off, scheduler-bypassing deployment, and `schedule_one_time` / `one_time_workflow_id` schedule a single deployment at a future epoch time. EdgeFlow-level monitoring alerts (`edgeflow_alert_offline_minutes`) can be set at the deployment-group level as a default and overridden per EdgeFlow.

## Endpoints

### `GET /1/deploymentCapacityClasses`

**List deployment capacity classes**

**Auth:** Bearer JWT required

Returns the list of deployment capacity classes available on the platform. A capacity class describes a Cogniac appliance hardware tier and the product variants associated with it. The list is the same for all tenants and is intended as a reference when inspecting or provisioning EdgeFlows.

The response has the shape `{"data": [DeploymentCapacityClassSchema, ...]}`. Some fields on each class are visible only to Cogniac support and administrative roles and are omitted for ordinary tenant callers.

**Errors:**
- `401` — missing or invalid Authorization header.

### `GET /1/deploymentCapacityClasses/{deployment_capacity_class_id}`

**Get a deployment capacity class**

**Auth:** Bearer JWT required

Retrieves a single deployment capacity class by id. Use this when you already know the id (for example, from a previous list call) and want to fetch its full record. As with the list endpoint, some fields are restricted to Cogniac support and administrative roles.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `deployment_capacity_class_id` | string | Identifier of the deployment capacity class. |

**Errors:**
- `401` — missing or invalid Authorization header.
- `404` — no deployment capacity class with the given id exists.

### `POST /1/deploymentGroups`

**Create a deployment group**

**Auth:** Bearer JWT required

Creates a new deployment group in the caller's tenant. The request body is validated against [DeploymentGroupSchema](#schema-deploymentgroupschema); `name` is required, all other fields are optional. The authenticated caller is automatically added to the group's `managers` list (in addition to any managers supplied in the request), and `created_by`, `created_at`, and the generated `deployment_group_id` are populated server-side. The response is the full, freshly-created deployment group.

If the caller supplies `next_workflow_id`, the workflow must already exist in the tenant — invalid workflow ids are rejected. If `edgeflow_alert_offline_minutes` is supplied, the tenant's `edgeflow_monitoring_sla` must be `Basic` or `Premium`; otherwise the request is rejected. The number of deployment groups a tenant can have may be capped by its contract.

Created groups have no EdgeFlows attached. Attach EdgeFlows by updating each EdgeFlow's `deployment_group_id` via the gateway/EdgeFlow API. Once EdgeFlows are attached, configure rollouts using `POST /1/deploymentGroups/{deployment_group_id}` or `POST /1/deploymentGroups/{deployment_group_id}/targetWorkflow`.

**Errors:**
- `400` — request body fails validation; `next_workflow_id` does not exist in the tenant; `edgeflow_alert_offline_minutes` is set but the tenant's monitoring SLA does not support alerts; the tenant has reached its contractually allowed maximum number of deployment groups.
- `401` — missing or invalid Authorization header.

### `GET /1/deploymentGroups/{deployment_group_id}`

**Get a deployment group**

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_viewer}`

Returns the deployment group identified by `deployment_group_id`. The response is a [DeploymentGroupSchema](#schema-deploymentgroupschema) object containing the group's configuration, current rollout state (`current_workflow_id`, `target_workflow_id`, `next_workflow_id`, `deploy_now_workflow_id`), schedule fields, managers, and audit timestamps.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `deployment_group_id` | string | Identifier of the deployment group. |

**Errors:**
- `401` — missing or invalid Authorization header.
- `403` — caller's roles do not include `cogniac_support`, `tenant_admin`, or `tenant_viewer`.
- `404` — no deployment group with the given id exists in the caller's tenant.

### `POST /1/deploymentGroups/{deployment_group_id}`

**Update a deployment group**

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_user}` (caller must additionally be listed as a manager on the deployment group, or hold `tenant_admin`)

Partially updates a deployment group. Any subset of the writable fields on [DeploymentGroupSchema](#schema-deploymentgroupschema) may be supplied; omitted fields are left unchanged. `modified_at` and `modified_by` are set automatically from the authenticated caller. Callers who are not in the group's `managers` list must additionally hold the `tenant_admin` role.

This endpoint is the primary control surface for workflow rollout:

- Setting `next_workflow_id` requests that the named workflow become the group's target. If the deployment group has no `scheduled_time` configured, the API immediately dispatches a deployment event to every EdgeFlow in the group and advances `target_workflow_id` to match. If a `scheduled_time` (cron) is configured, the scheduler picks up `next_workflow_id` on the next tick.
- Setting `deploy_now_workflow_id` triggers an immediate one-off rollout of that workflow to every EdgeFlow in the group, independent of the scheduler. Setting `deploy_now_workflow_id` to `null` cancels an in-flight deploy-now.
- Setting `target_workflow_id` (or, for backwards compatibility, `current_workflow_id`) to the same value it already has redeploys that workflow. Setting either to `null` removes the workflow from the deployment group, clearing `current_workflow_id`, `target_workflow_id`, and `next_workflow_id`.
- Setting `scheduled_time` to a cron expression schedules recurring deployments; setting `schedule_one_time` (epoch seconds) together with `one_time_workflow_id` schedules a single future deployment.

When a deployment is dispatched immediately, the supplied `next_workflow_id` or `deploy_now_workflow_id` must already exist in the tenant. If any EdgeFlow in the group fails to accept the deployment event, the call returns an error and reports the failure count; the caller can retry by setting the workflow id again.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `deployment_group_id` | string | Identifier of the deployment group. |

**Errors:**
- `400` — request body fails validation; `next_workflow_id`, `deploy_now_workflow_id`, or `target_workflow_id` references a workflow that does not exist in the tenant; `edgeflow_alert_offline_minutes` is set but the tenant's monitoring SLA does not support alerts; one or more EdgeFlows in the group failed to accept the immediate deployment event.
- `401` — missing or invalid Authorization header.
- `403` — caller is not a manager of the deployment group and does not hold `tenant_admin`; or caller's roles do not include `cogniac_support`, `tenant_admin`, or `tenant_user`.
- `404` — no deployment group with the given id exists in the caller's tenant.

### `DELETE /1/deploymentGroups/{deployment_group_id}`

**Delete a deployment group**

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_user}` (caller must additionally be listed as a manager on the deployment group, or hold `tenant_admin`)

Permanently deletes the deployment group. Returns `204 No Content` on success. Callers who are not in the group's `managers` list must additionally hold the `tenant_admin` role.

A deployment group cannot be deleted while any EdgeFlows are attached to it. To delete a group with attached EdgeFlows, first reassign or clear `deployment_group_id` on each EdgeFlow via the gateway/EdgeFlow API.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `deployment_group_id` | string | Identifier of the deployment group. |

**Errors:**
- `401` — missing or invalid Authorization header.
- `403` — caller is not a manager of the deployment group and does not hold `tenant_admin`; or caller's roles do not include `cogniac_support`, `tenant_admin`, or `tenant_user`.
- `404` — no deployment group with the given id exists in the caller's tenant.
- `412` — one or more EdgeFlows are still attached to the deployment group.

### `GET /1/deploymentGroups/{deployment_group_id}/gateways`

**List EdgeFlows in a deployment group**

**Auth:** Bearer JWT required

Returns every EdgeFlow currently attached to the deployment group, as `{"data": [GatewaySchema, ...]}`. Each entry is a [GatewaySchema](#schema-gatewayschema) describing the EdgeFlow's identity, network configuration, deployment status, and (for permitted roles) setup credentials. The list is sorted by name.

An optional `reverse=true` query parameter reverses the sort order. To attach or detach an EdgeFlow from a deployment group, update the EdgeFlow's `deployment_group_id` via the gateway/EdgeFlow API.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `deployment_group_id` | string | Identifier of the deployment group. |

**Errors:**
- `401` — missing or invalid Authorization header.
- `404` — no deployment group with the given id exists in the caller's tenant.

### `GET /1/deploymentGroups/{deployment_group_id}/history`

**Retrieve deployment history for a deployment group**

**Auth:** Bearer JWT required

Returns the audit trail of workflow deployments applied to this deployment group. Each entry is a [DeploymentHistorySchema](#schema-deploymenthistoryschema) recording the workflow id, the time of deployment, and the user that initiated it. Results are paginated; the response shape is `{"data": [...], "last_key": <opaque-cursor>}`. Pass the returned `last_key` as the `last_key` query parameter on the next call to fetch the next page.

Query parameters are validated against [DeploymentHistoryQuerySchema](#schema-deploymenthistoryqueryschema) and include `start` and `end` (epoch seconds) to bound the time range, `limit` to cap the page size, and `reverse` to flip ordering.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `deployment_group_id` | string | Identifier of the deployment group. |

**Errors:**
- `400` — query parameters fail validation.
- `401` — missing or invalid Authorization header.
- `404` — no deployment group with the given id exists in the caller's tenant.

### `POST /1/deploymentGroups/{deployment_group_id}/prepull/{workflow_id}`

**Pre-pull a workflow's container images on every EdgeFlow in a deployment group**

**Auth:** Bearer JWT required

Asks every EdgeFlow attached to the deployment group to begin downloading (pre-pulling) the container images required by `workflow_id`, so that a subsequent deployment of that workflow can proceed without waiting on image transfer. Returns once the pre-pull has been requested; pre-pull progress can be polled via `GET /1/deploymentGroups/{deployment_group_id}/prepull`.

This endpoint is useful before scheduling a large rollout to a fleet of bandwidth-constrained EdgeFlows: pre-pull first, then deploy.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `deployment_group_id` | string | Identifier of the deployment group. |
| `workflow_id` | string | Identifier of the workflow whose container images should be pre-pulled. |

**Errors:**
- `401` — missing or invalid Authorization header.
- `404` — no deployment group with the given id exists in the caller's tenant, or no workflow with the given id exists in the caller's tenant.

### `GET /1/deploymentGroups/{deployment_group_id}/prepull`

**Get pre-pull status for every EdgeFlow in a deployment group**

**Auth:** Bearer JWT required

Returns the most recent pre-pull status reported by each EdgeFlow attached to the deployment group, as `{"data": [{"gateway_id": ..., "status": ...}, ...]}`. The `status` field is the EdgeFlow's most recent pre-pull subsystem status payload, or `null` if the EdgeFlow has not yet reported a pre-pull status. Use this after `POST .../prepull/{workflow_id}` to monitor pre-pull progress across the fleet.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `deployment_group_id` | string | Identifier of the deployment group. |

**Errors:**
- `401` — missing or invalid Authorization header.
- `404` — no deployment group with the given id exists in the caller's tenant.

### `POST /1/deploymentGroups/{deployment_group_id}/targetWorkflow`

**Set the target workflow on a deployment group**

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_user}` (caller must additionally be listed as a manager on the deployment group, or hold `tenant_admin`)

Directly sets `target_workflow_id` on the deployment group without dispatching any deployment events. Use this to record an intended target — for example, when an external orchestrator manages rollout — without triggering the immediate-deployment behavior of `POST /1/deploymentGroups/{deployment_group_id}`. `modified_at` and `modified_by` are updated automatically.

The request body must include `target_workflow_id`, and that workflow must already exist in the caller's tenant. Callers who are not in the group's `managers` list must additionally hold the `tenant_admin` role.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `deployment_group_id` | string | Identifier of the deployment group. |

**Errors:**
- `400` — `target_workflow_id` is missing from the request body, or references a workflow that does not exist in the caller's tenant.
- `401` — missing or invalid Authorization header.
- `403` — caller is not a manager of the deployment group and does not hold `tenant_admin`; or caller's roles do not include `cogniac_support`, `tenant_admin`, or `tenant_user`.
- `404` — no deployment group with the given id exists in the caller's tenant.
