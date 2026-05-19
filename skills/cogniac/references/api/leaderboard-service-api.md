# leaderboard-service-api

Surface the current leaderboard for a Cogniac application: the ranked set of trained models and their per-evaluation-metric scores against the most recent shared consensus release.

As models are retrained against new feedback, the platform periodically publishes a "consensus release" — a snapshot of evaluation-metric scores that lets users compare candidate models on the same ground-truth data. This service reads those snapshots and returns the most recent one whose per-metric results are all aligned to the same `consensus_release_id`, so callers see a coherent, comparable view of model performance.

The typical consumer is the Cogniac UI's application leaderboard view, but any client that needs to programmatically inspect ranked model performance for an application can call the endpoint directly. All endpoints are served under the `/22` API version prefix.

## Endpoints

### `GET /22/leaderboard/version`

Return the service's running API version. Intended for health-check and version-pinning use.

**Auth:** no auth required

**Responses:**

| Status | Description |
|---|---|
| 200 | `{ "api_version": 22 }` |

### `GET /22/applications/{application_id}/leaderboard/recent_consensus_snapshot`

Return the most recent consensus snapshot for the given application in which every active evaluation metric's snapshot shares the same `consensus_release_id`. The response includes the ranked list of model snapshots, the evaluation metrics they were scored against, and the identifying timestamps for the consensus release the results came from.

By default the response is filtered to the application's primary evaluation metric and trimmed to the top-ranked models, with each model annotated with its `primary_metric_rank`. Set `eval_metrics=all` to consider every active evaluation metric on the application, and `output_format=debug` to receive the raw, unranked snapshot rows and evaluation-metric records (intended for troubleshooting).

When a leaderboard cannot be produced yet — typically because the application has not finished evaluating its current models against a full consensus release — the endpoint returns `202` with a message indicating that leaderboard information is not yet available. This is a transient condition; the caller may retry later.

**Auth:** Bearer JWT required

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `application_id` | path | string | **yes** | Identifier of the application whose leaderboard should be returned. |
| `set_assignment` | query | string | no | Which evaluation set the snapshot scores are drawn from. One of `training`, `validation`. Defaults to `validation`. |
| `snapshot_type` | query | string | no | Which snapshot variant to return. One of `regular`, `int8` (TRT INT8-quantized). Defaults to `regular`. |
| `output_format` | query | string | no | One of `public` (default; refactored, ranked, top-N trimmed) or `debug` (raw snapshot rows and evaluation-metric records). |
| `eval_metrics` | query | string | no | One of `primary` (default; restrict to the application's primary evaluation metric) or `all` (consider every active evaluation metric on the application). |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Leaderboard payload: `app_id`, `leaderboard_timestamp`, ranked `snapshot` list, `evaluation_metrics`, `primary_evaluation_metric_hash`, `consensus_release_id`, `consensus_release_timestamp`. | `application/json` → any |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 202 | A consensus release snapshot covering all active evaluation metrics is not yet ready for the application, or refactoring produced no usable rows (e.g., the application still has only an initial/donor model with no evaluation results), or the primary evaluation metric was missing from the available snapshot results. |
| 401 | Missing Bearer token in Authorization header. |
| 404 | No active evaluation metrics are configured for the application, or `eval_metrics=primary` was requested and the application has no active primary evaluation metric. |

---

## Schema Components

All Pydantic-derived schemas referenced above. Constraints (enum, range, length, pattern, default) are inline so an API consumer can write a correct client without reading Pydantic source.

### `HTTPValidationError` <a id='schema-httpvalidationerror'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `detail` | list[[ValidationError](#schema-validationerror)] | no |  |  |

### `ValidationError` <a id='schema-validationerror'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `ctx` | object | no |  |  |
| `input` | any | no |  |  |
| `loc` | list[string \| integer] | **yes** |  |  |
| `msg` | string | **yes** |  |  |
| `type` | string | **yes** |  |  |
