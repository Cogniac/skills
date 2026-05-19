# edgeflow-core-api

The EdgeFlow Core API manages the lifecycle and runtime control of EdgeFlow appliances — Cogniac's on-prem GPU devices that run inference at the edge. Use it to register a new EdgeFlow in your tenant, update its configuration (managers, deployment group, model deployment policy, NTP/UPS, network interfaces, TLS certificate), retrieve its current state and historical subsystem status, manage attached GigE Vision (GenICam) network cameras, and send operational events such as `reboot`, `upgrade`, `factory_reset`, `ping`, `flush_upload_queue`, `time_bound_media_upload`, `trigger_camera_capture`, and `capture_trigger`.

Each EdgeFlow is scoped to exactly one tenant. Most write operations are restricted to the EdgeFlow's *managers* — users explicitly listed on the EdgeFlow object — or to tenant administrators. An EdgeFlow can be placed in a configuration-locked state (`lock: true`); while locked, updates and lifecycle events (reboot, upgrade, factory reset, etc.) are rejected until the lock is cleared.

## Authentication

All endpoints require a Bearer JWT acquired through the Cogniac authentication flow and bound to a specific tenant (`tenant_id`). Role requirements are noted per endpoint. Requests with a missing or invalid Authorization header return `401`. Requests whose token does not carry a sufficient role return `403`.

## Conventions

- All timestamps are seconds since the Unix epoch as JSON numbers (may be fractional).
- Path identifiers (`gw_id`, `gateway_id`) refer to the same EdgeFlow identifier returned by `POST /1/gateways` as `gateway_id`.
- Successful event-dispatch endpoints (`POST /1/gateways/{gw_id}/event/...`) return `204 No Content`. The event is queued for asynchronous delivery to the EdgeFlow; a `204` response confirms acceptance, not execution on the device.
- Some endpoints expose responses that vary depending on the caller's roles (for example, `setup_password` and `setup_ssh_key` on the EdgeFlow object). Fields the caller is not entitled to see are omitted.

## Endpoints

### `POST /1/gateways`

**Creates an EdgeFlow**

Registers a new EdgeFlow in the caller's tenant. The request body must include at minimum a `name` and a `model`; see [`GatewaySchema`](#schema-gatewayschema) for the full set of accepted fields. On success the response is the newly-created EdgeFlow object, including the server-assigned `gateway_id`. The calling user is automatically added to the EdgeFlow's `managers` list.

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_user}`

**Errors:**

| Status | Condition |
|---|---|
| 400 | Request body fails validation; `input_subject_uids` reference subjects outside the caller's tenant; `managers` reference users that are not members of the tenant. |
| 401 | Missing or invalid Authorization header. |
| 403 | Caller lacks one of the required roles. |

### `POST /1/gateways/{gw_id}`

**Updates an EdgeFlow**

Partially updates fields on an existing EdgeFlow. Only the fields included in the request body are modified. Updates are permitted only for users listed in the EdgeFlow's `managers`, tenant administrators, or the EdgeFlow itself.

If the EdgeFlow is configuration-locked (`lock: true`), updates are rejected unless the same request also sets `lock` to `false`. When the EdgeFlow is bound to a deployment group, applying changes that affect deployment causes the configured workflow to be re-applied to the device.

**Auth:** Bearer JWT; required roles: `{cogniac_support, ef_device, tenant_admin, tenant_ops, tenant_user}` (caller must also be listed in the EdgeFlow's `managers`, or hold `tenant_admin` or `ef_device`)

**Path params:**

| Name | Type | Description |
|---|---|---|
| `gw_id` | string | EdgeFlow identifier. |

**Errors:**

| Status | Condition |
|---|---|
| 400 | Body fails validation; `input_subject_uids` outside tenant; `managers` outside tenant; the update is rejected due to a configuration lock. |
| 401 | Missing or invalid Authorization header. |
| 404 | EdgeFlow not found in the caller's tenant, or caller is not an EdgeFlow manager. |

### `DELETE /1/gateways/{gw_id}`

**Deletes an EdgeFlow**

Removes the EdgeFlow from the tenant. Status history is purged asynchronously and any installed TLS key/certificate pair is deleted. Deletion is permitted only for users listed in the EdgeFlow's `managers` or tenant administrators, and is rejected while the EdgeFlow is configuration-locked. Returns `204 No Content` on success.

**Auth:** Bearer JWT required (caller must be listed in the EdgeFlow's `managers`, or hold `tenant_admin` or `ef_device`)

**Path params:**

| Name | Type | Description |
|---|---|---|
| `gw_id` | string | EdgeFlow identifier. |

**Errors:**

| Status | Condition |
|---|---|
| 400 | EdgeFlow is configuration-locked. |
| 401 | Missing or invalid Authorization header. |
| 404 | EdgeFlow not found in the caller's tenant, or caller is not an EdgeFlow manager. |

### `GET /1/gateways/{gw_id}`

**Retrieves an EdgeFlow**

Returns the EdgeFlow object identified by `gw_id` in the caller's tenant, including the current depth of its event queue (`event_queue_count`) and, when a TLS certificate has been installed, the PEM-encoded certificate bytes within `tls_cert_metadata.certificate`.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `gw_id` | string | EdgeFlow identifier. |

**Errors:**

| Status | Condition |
|---|---|
| 401 | Missing or invalid Authorization header. |
| 404 | EdgeFlow not found in the caller's tenant. |

### `GET /1/gateways/{id}/networkCameras`

**Lists network cameras attached to an EdgeFlow**

Returns the GigE Vision network cameras discovered by the specified EdgeFlow, sorted by `camera_name`.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | EdgeFlow identifier. |

### `POST /1/gateways/{id}/networkCameras`

**Sets the active state of network cameras attached to an EdgeFlow**

Enables or disables one or more network cameras attached to the specified EdgeFlow. The request body specifies the cameras to update (by `network_camera_id`, or the literal `"all"`) and the target `active` boolean.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | EdgeFlow identifier. |

### `GET /1/gateways/{gw_id}/status/{subsystem_name}`

**Lists status records for a specific EdgeFlow subsystem**

Returns historical status records reported for a named subsystem of the EdgeFlow. Supports pagination; when more results are available, the response includes `paging.next`.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `gw_id` | string | EdgeFlow identifier. |
| `subsystem_name` | string | Subsystem to query. |

**Errors:**

| Status | Condition |
|---|---|
| 400 | `start` or `end` is negative, or `end` precedes `start`. |
| 401 | Missing or invalid Authorization header. |
| 404 | EdgeFlow not found in the caller's tenant. |

### `POST /1/gateways/{gw_id}/status/{subsystem_name}`

**Records a status entry for an EdgeFlow subsystem**

Appends a status record for the named subsystem of the specified EdgeFlow.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `gw_id` | string | EdgeFlow identifier. |
| `subsystem_name` | string | Subsystem to record status for. |

### `GET /1/gateways/{gw_id}/status`

**Lists status records for an EdgeFlow**

Returns historical status records reported for the EdgeFlow across all subsystems. Pass a `subsystem` query parameter to restrict to a single subsystem.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `gw_id` | string | EdgeFlow identifier. |

### `POST /1/gateways/{gw_id}/status`

**Updates an EdgeFlow's current status snapshot**

Sets the EdgeFlow's `current_status` to the supplied JSON-serialized status string; the prior value is moved to `previous_status`. Returns `204 No Content` on success.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `gw_id` | string | EdgeFlow identifier. |

### `POST /1/gateways/{gw_id}/event/capture_trigger/{capture_app_id}`

**Triggers a camera-capture application on an EdgeFlow**

Queues a `capture_trigger` event for the specified camera-capture application on the EdgeFlow.

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_ops, tenant_user}`

### `POST /1/gateways/{gw_id}/event/factory_reset`

**Queues a `factory_reset` event**

The device will restore itself to factory defaults when it consumes the event. Rejected while the EdgeFlow is configuration-locked.

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_ops, tenant_user}` (caller must also be listed in the EdgeFlow's `managers`, or hold `tenant_admin` or `ef_device`)

### `POST /1/gateways/{gw_id}/event/flush_upload_queue`

**Queues a `flush_upload_queue` event**

Instructs the EdgeFlow to flush queued media uploads. The request body supports modes: `start_time` only, `end_time` only, both (must satisfy `start_time < end_time`), or neither (flush everything).

**Auth:** Bearer JWT; required roles: `{tenant_admin}`

### `POST /1/gateways/{gw_id}/event/reboot`

**Queues a `reboot` event**

The optional `reboot_time` (Unix-epoch seconds) schedules the reboot for a future time; if omitted, the EdgeFlow reboots when it next consumes the event.

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_ops, tenant_user}` (caller must also be listed in the EdgeFlow's `managers`, or hold `tenant_admin` or `ef_device`)

### `POST /1/gateways/{gw_id}/event/upgrade`

**Queues an `upgrade` event**

Instructs the EdgeFlow to install the specified `software_version`. If `reboot` is true the device reboots into the new version after applying the upgrade. Rejected while configuration-locked.

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_ops, tenant_user}` (caller must also be listed in the EdgeFlow's `managers`, or hold `tenant_admin` or `ef_device`)

### `POST /1/gateways/{gw_id}/event/set_boot_software_version`

**Queues a `set_boot_software_version` event**

Instructs the EdgeFlow to set its boot software to the specified `software_version`. Rejected while configuration-locked.

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin}`

### `POST /1/gateways/{gw_id}/event/start_reverse_ssh_tunnel`

**Queues a `start_reverse_ssh_tunnel` event**

Instructs the EdgeFlow to open an outbound reverse SSH tunnel to a customer-controlled host, enabling temporary remote access for diagnostics. The body provides the SSH endpoint, username, private key, and remote port.

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin}`

### `POST /1/gateways/{gw_id}/event/ping`

**Queues a `ping` event**

Useful for testing reachability and event delivery. The optional `ping_id` is echoed in EdgeFlow logs for correlation.

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin}`

### `POST /1/gateways/{gw_id}/event/trigger_camera_capture`

**Queues a `trigger_camera_capture` event**

Triggers camera capture on the EdgeFlow. Provide `subject_uid` to trigger all camera-capture applications associated with a specific subject. The optional `trigger_domain_unit` (under 80 characters) tags the resulting capture(s).

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_user}`

### `POST /1/gateways/{gw_id}/event/time_bound_media_upload`

**Queues a time-bound media upload event**

Instructs the EdgeFlow to upload media captured within the specified time range `[start_time, end_time]` (Unix-epoch seconds). Both bounds are required and `start_time` must precede `end_time`.

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin}`

### `POST /1/gateways/{gateway_id}/certificate`

**Installs a TLS certificate on an EdgeFlow**

Installs a customer-supplied PEM-encoded TLS certificate chain and matching private key. The certificate is validated before installation: the private key must pass an OpenSSL consistency check, the chain must parse, the leaf certificate must be currently valid, must remain valid for at least three weeks, must have a Common Name, and must match the supplied private key.

**Auth:** Bearer JWT; required roles: `{tenant_admin}`

### `GET /1/gateways/{gateway_id}/certificate`

**Retrieves the TLS certificate metadata for an EdgeFlow**

Returns metadata for the TLS certificate installed on the EdgeFlow, including validity window, issuer, fingerprint, domain name, and the PEM-encoded certificate bytes.

**Auth:** Bearer JWT; required roles: `{tenant_admin}`

### `DELETE /1/gateways/{gateway_id}/certificate`

**Removes the TLS certificate from an EdgeFlow**

Deletes the installed TLS certificate, private key, and metadata. The EdgeFlow is notified of the change.

**Auth:** Bearer JWT; required roles: `{tenant_admin}`
