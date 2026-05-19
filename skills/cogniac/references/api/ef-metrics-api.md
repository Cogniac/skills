# ef-metrics-api

Read time-series metrics for your EdgeFlow appliances and CloudFlow deployments. The service exposes Cogniac's metrics store as a small, query-only API so dashboards, monitoring integrations, and operations tooling can pull recent measurements for a tenant or for an individual EdgeFlow.

Three endpoints are available. `GET /1/metrics_name` returns the catalog of metric names that are currently being recorded. `GET /1/metrics` returns the time series for a named metric across an entire tenant. `GET /1/metrics/ef` narrows the same query to a single EdgeFlow appliance (`ef_id`). All time-series responses are returned in a Grafana-compatible shape: a list of series, each with a `metric` label set and a sorted list of `[timestamp_seconds, value]` pairs.

Time ranges are specified in Unix epoch seconds via `start` and `end`. Either supply both bounds or neither; when both are omitted the API returns the most recent twelve hours of data. The metrics store is hosted in a single Cogniac region — requests to other regional endpoints are transparently forwarded so callers can use the host they normally use for the Cogniac API.

## Endpoints

### `GET /1/metrics`

Return the time series for a named metric across a tenant. The response is a Grafana-compatible list of series, where each series carries the labels recorded with the sample (for example `tenant_id`, `ef_id`, and any metric-specific dimensions) and a sorted list of `[timestamp_seconds, value]` pairs covering the requested window.

If `start` and `end` are both omitted, the most recent twelve hours of data are returned. If only one of them is supplied, the request is rejected. When the metric has no samples in the window, the response is `204 No Content`.

**Auth:** Bearer JWT; required roles: `{ef_ops, tenant_admin, tenant_creator, tenant_user, tenant_viewer}`

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `metric_name` | query | string | **yes** | Name of the metric to query. Use `GET /1/metrics_name` to discover available names. |
| `tenant_id` | query | string | **yes** | Identifier of the tenant whose metrics should be returned. |
| `start` | query | integer \| null | no | Start of the query window in Unix epoch seconds. Must be supplied together with `end`. |
| `end` | query | integer \| null | no | End of the query window in Unix epoch seconds. Must be supplied together with `start`. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Time-series payload with `status` and a Grafana-formatted `data` array of `{metric, values}` entries. | `application/json` → any |
| 204 | No samples were recorded for the metric in the requested window. | — |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 400 | `start` and `end` were not both supplied, or `start` is greater than `end`. |
| 500 | The metrics backend could not be reached. |
| 5xx | The metrics backend returned an error; the upstream status code and detail are propagated. |

### `GET /1/metrics/ef`

Return the time series for a named metric scoped to a single EdgeFlow appliance within a tenant. The response shape, time-window semantics, and empty-result behavior match `GET /1/metrics`; the added `ef_id` constraint filters samples to the chosen appliance.

Use this endpoint when building per-appliance dashboards or alerting — for example to chart inference throughput, queue depth, or device health on one EdgeFlow in isolation.

**Auth:** Bearer JWT; required roles: `{ef_ops, tenant_admin, tenant_creator, tenant_user, tenant_viewer}`

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `metric_name` | query | string | **yes** | Name of the metric to query. Use `GET /1/metrics_name` to discover available names. |
| `tenant_id` | query | string | **yes** | Identifier of the tenant that owns the appliance. |
| `ef_id` | query | string | **yes** | Identifier of the EdgeFlow appliance to scope the query to. |
| `start` | query | integer \| null | no | Start of the query window in Unix epoch seconds. Must be supplied together with `end`. |
| `end` | query | integer \| null | no | End of the query window in Unix epoch seconds. Must be supplied together with `start`. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Time-series payload with `status` and a Grafana-formatted `data` array of `{metric, values}` entries. | `application/json` → any |
| 204 | No samples were recorded for the metric and appliance in the requested window. | — |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 400 | `start` and `end` were not both supplied, or `start` is greater than `end`. |
| 500 | The metrics backend could not be reached. |
| 5xx | The metrics backend returned an error; the upstream status code and detail are propagated. |

### `GET /1/metrics_name`

List the metric names currently available for query. Use the returned names as the `metric_name` argument to `GET /1/metrics` and `GET /1/metrics/ef`.

The set of metrics evolves over time as new measurements are added to the platform, so callers building dashboards should refresh this list periodically rather than hard-coding metric names.

**Auth:** Bearer JWT; required roles: `{ef_ops, tenant_admin, tenant_creator, tenant_user, tenant_viewer}`

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Object with `status` and a `data` array of metric-name strings. | `application/json` → any |

**Errors:**

| Status | Condition |
|---|---|
| 500 | The metrics backend could not be reached. |
| 5xx | The metrics backend returned an error; the upstream status code and detail are propagated. |

---

## Schema Components

All Pydantic-derived schemas referenced above. Constraints (enum, range, length, pattern, default) are inline so an API consumer can write a correct client without reading Pydantic source.

### `HTTPValidationError` <a id='schema-httpvalidationerror'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `detail` | list[[ValidationError](#schema-validationerror)] | no |  | One entry per failed validation rule. |

### `ValidationError` <a id='schema-validationerror'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `ctx` | object | no |  | Additional context about the validation failure. |
| `input` | any | no |  | The input value that failed validation. |
| `loc` | list[string \| integer] | **yes** |  | Path to the offending field, as a sequence of keys and indices. |
| `msg` | string | **yes** |  | Human-readable explanation of the validation failure. |
| `type` | string | **yes** |  | Machine-readable validation-error code. |
