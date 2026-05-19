# consensus-release-core-api

Inspect the consensus release artifacts produced for a Cogniac application. A consensus release is a frozen snapshot of the labeled training data for an application's output subjects — it pairs each piece of media (and any region-of-interest focus) with the human-aggregated verdict that won consensus among reviewers, together with the upstream model assertions and the per-subject detection records that contributed to it. Each release carries a stable `consensus_release_id` and the statistics describing how many items, media focuses, and fully-labeled focuses are present.

These endpoints let an authorized caller list the consensus releases that have been published for a given application, fetch the metadata and statistics for a specific release, download the full release contents (the per-item consensus records, optionally joined with media descriptors), and retrieve the upstream model assertions that fed into the consensus computation. A separate `consensus_detection_release` endpoint joins consensus-detection records from the application's output subjects with the most recent assertions from the application's currently winning model so the caller can correlate the two views by media id.

All endpoints are served under the `/22` API version prefix.

## Endpoints

### `GET /22/version`

Return the running build identifier of the service. Intended for container health checks.

**Auth:** Bearer JWT required

**Responses:**

| Status | Description |
|---|---|
| 200 | `{ "version": "<build identifier>" }` |

### `GET /22/applications/{app_id}/consensus_release`

List the consensus releases that have been published for the application, most recent first. Each item carries the `consensus_release_id`, its timestamp, and the per-release item counts. Use `limit` plus the returned `next_page_token` to page through additional releases; `next_page_token` is `null` once the listing is exhausted.

**Auth:** Bearer JWT; required roles: `{cogniac_admin, cogniac_dev}`

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `app_id` | path | string | **yes** | Identifier of the application whose consensus releases are listed. |
| `limit` | query | integer | no | Maximum number of releases to return in this page (minimum `1`, default `10`). |
| `next_page_token` | query | string | no | Opaque cursor returned by a previous call. Omit to start at the most recent release. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Page of consensus releases for the application. | `application/json` → [AppConsensuReleaseApiResponse](#schema-appconsensureleaseapiresponse) |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 400 | `next_page_token` could not be decoded. |
| 404 | Application not found, or the underlying release store rejected the request. |
| 500 | Unexpected failure while looking up application consensus releases or validating the application. |

### `GET /22/applications/{app_id}/consensus_release/{consensus_release_id}`

Return the metadata and statistics for a single consensus release. The statistics block reports the per-set consensus-item counts as well as the media-focus and fully-labeled media-focus counts captured at the time the release was frozen.

**Auth:** Bearer JWT; required roles: `{cogniac_admin, cogniac_dev}`

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `app_id` | path | string | **yes** | Identifier of the application the release belongs to. |
| `consensus_release_id` | path | string | **yes** | Identifier of the consensus release whose metadata is being fetched. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Metadata and statistics for the consensus release. | `application/json` → [ConsensusReleaseMetadataApiResponse](#schema-consensusreleasemetadataapiresponse) |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 404 | Application not found, no consensus release exists with the supplied `app_id` and `consensus_release_id`, or the release lookup raised a value error. |
| 500 | Unexpected failure while retrieving the consensus release metadata or validating the application. |

### `GET /22/applications/{app_id}/consensus_release/{consensus_release_id}/consensus_items`

Download the full set of consensus items in a release. Each item contains the consensus verdict for one media-focus pair across the application's output subjects. By default the response is "abridged" — each item carries only the identifiers needed to correlate with other sources. Set `abriged_media=false` to include the full media descriptor with each item.

**Auth:** Bearer JWT; required roles: `{cogniac_admin, cogniac_dev}`

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `app_id` | path | string | **yes** | Identifier of the application the release belongs to. |
| `consensus_release_id` | path | string | **yes** | Identifier of the consensus release to download. |
| `abriged_media` | query | boolean | no | When `true` (default), each consensus item omits the full media descriptor. Set to `false` to receive items joined with their media records. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | JSON array of consensus items for the release. | `application/json` → any |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 404 | Application not found, or the release could not be located in the consensus store. |
| 500 | Unexpected failure while downloading the consensus release or validating the application. |

### `GET /22/applications/{app_id}/consensus_release/{consensus_release_id}/upstream_assertions`

Return the upstream model assertions that fed into the named consensus release. These are the per-item assertions captured from the input pipeline just prior to consensus aggregation; they are useful for auditing how individual upstream contributions shaped the consensus verdict.

**Auth:** Bearer JWT; required roles: `{cogniac_admin, cogniac_dev}`

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `app_id` | path | string | **yes** | Identifier of the application the release belongs to. |
| `consensus_release_id` | path | string | **yes** | Identifier of the consensus release whose upstream assertions are being fetched. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | JSON array of upstream assertions associated with the consensus release. | `application/json` → any |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 404 | Application not found. |
| 500 | Unexpected failure while validating the application. |

### `GET /22/applications/{app_id}/consensus_detection_release`

Return a combined view of the application's consensus-detection records and the assertions from the application's currently winning model. For each of the application's output subjects, the service collects the published consensus-detection records and concatenates them with the training-set assertions from the top-ranked model for that subject (as ranked by the application's primary evaluation metric). The result is a flat JSON array; the two record formats differ, but `media_id` values can be used to match an entry in one source against an entry in the other.

This endpoint loads the combined result into memory before responding; very large applications may produce large responses.

**Auth:** Bearer JWT; required roles: `{cogniac_admin, cogniac_dev}`

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `app_id` | path | string | **yes** | Identifier of the application whose consensus detections and model assertions are joined. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Combined list of consensus-detection records and winning-model assertions. | `application/json` → any |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 404 | Application not found. |
| 500 | Unexpected failure while validating the application. |

---

## Schema Components

All Pydantic-derived schemas referenced above. Constraints (enum, range, length, pattern, default) are inline so an API consumer can write a correct client without reading Pydantic source.

### `AppConsensuReleaseApiResponse` <a id='schema-appconsensureleaseapiresponse'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `consensus_releases` | list[[ConsensusReleaseItem](#schema-consensusreleaseitem)] | **yes** |  | Page of consensus releases belonging to the application, ordered most recent first. |
| `next_page_token` | string \| null | **yes** |  | Opaque cursor to pass as `next_page_token` on a subsequent call to fetch the next page, or `null` when no further pages remain. |

### `ConsensusReleaseItem` <a id='schema-consensusreleaseitem'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `consensus_release_id` | string | **yes** |  | Stable identifier for the consensus release. |
| `consensus_release_timestamp` | string | **yes** | pattern='^(?!^[-+.]*$)[+-]?0*\\d*\\.?\\d*$' | Time at which the consensus release was frozen, serialized as a decimal-formatted string. |
| `statistics` | dict[str, any] | **yes** |  | Per-release summary statistics (for example, item counts by set assignment). |

### `ConsensusReleaseMetadataApiResponse` <a id='schema-consensusreleasemetadataapiresponse'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `app_id` | string | **yes** |  | Identifier of the application the release belongs to. |
| `consensus_release_id` | string | **yes** |  | Identifier of the consensus release being described. |
| `statistics` | [ConsensusReleaseStatistics](#schema-consensusreleasestatistics) | **yes** |  | Statistics captured for the release at the time it was frozen. |

### `ConsensusReleaseStatistics` <a id='schema-consensusreleasestatistics'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `consensus_items_counts` | dict[str, any] | **yes** |  | Counts of consensus items broken out by set assignment (for example, training / validation / test). |
| `media_focus_counts` | dict[str, any] | **yes** |  | Counts of distinct media-focus pairs included in the release. |
| `media_focus_fully_labeled_counts` | dict[str, any] | **yes** |  | Counts of media-focus pairs that are fully labeled across all output subjects in the release. |

### `HTTPValidationError` <a id='schema-httpvalidationerror'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `detail` | list[[ValidationError](#schema-validationerror)] | no |  | One entry per failed validation check, identifying the offending field and the reason it failed. |

### `ValidationError` <a id='schema-validationerror'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `ctx` | object | no |  | Optional structured context for the validation error. |
| `input` | any | no |  | The input value that triggered the error, when available. |
| `loc` | list[string \| integer] | **yes** |  | Location of the failing field within the request (path segments and array indices). |
| `msg` | string | **yes** |  | Human-readable description of the validation failure. |
| `type` | string | **yes** |  | Machine-readable error type identifier. |
