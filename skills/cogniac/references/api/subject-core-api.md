# subject-core-api

Subjects are the primary way to organize, label, and route media through the Cogniac platform. A subject represents a user-defined concept — anything from a simple tag like `cat` to a more complex notion like `cat with mouse in mouth`, or a logical grouping such as `lobby security camera feed`. Subjects also define the input and output of applications: media flows into an application through one or more input subjects and emerges associated with one or more output subjects, with a probability that reflects how strongly the model (or a user's feedback) believes the subject is present.

This service exposes the subject lifecycle and the subject-media association layer that sits underneath it. Use it to create and manage subjects, associate or disassociate media with a subject, retrieve the per-association detection history (model predictions and user feedback that contributed to the current association), and read the consensus count history that drives training data selection. A subject-media association carries a probability in `[0, 1]` (1 = strongly associated, 0 = strongly not associated, 0.5 = uncertain) and, once enough feedback accumulates to bring uncertainty below the consensus threshold, a `consensus` value of `True`, `False`, or `Sidelined`. Consensus associations are what the platform uses as labeled training examples.

All endpoints require a tenant-scoped Bearer token (see the authentication section of the Cogniac API overview). Subjects are scoped to the calling tenant by default, but a subject can be marked `public_read` or `public_write` so that other tenants can read or contribute media to it; cross-tenant access is allowed only through that mechanism and via shared-subject grants. A subject that is bound as the input or output of any application cannot be deleted until it is unbound, and a subject that is linked to a network camera cannot be deleted while that link exists.

## Endpoints

### `POST /1/subjects`

**Create a subject**

Create a new subject in the caller's tenant. The caller becomes the `created_by` user and the subject is initially scoped to the caller's tenant.

A subject's `public_read` flag controls whether other tenants can read it and use it for queries; `public_write` controls whether other tenants can associate their own media with it. Setting `public_write` implies `public_read` — a publicly writeable subject is automatically made publicly readable. Visibility cannot be tightened later: a publicly readable or writeable subject cannot be made private (see the update endpoint).

The optional `expires_in` value (in months) controls automatic expiration of non-consensus subject-media associations. If unset, the tenant's default expiration is applied. Consensus associations are never expired by this mechanism.

The response is the newly created subject including the server-assigned `subject_uid`, `created_by`, `created_at`, `modified_at`, and `tenant_id`.

**Auth:** Bearer JWT required

**Request body:** [SubjectSchema](#schema-subjectschema)

**Errors:**

- `400` — request body fails validation (e.g. invalid `name`, invalid `custom_data`, malformed `expires_in`).
- `401` — missing or invalid Authorization header.
- `422` — schema validation error.

### `POST /1/subjects/{subject_uid}`

**Update a subject**

Update mutable fields on an existing subject. Only the fields present in the request body are modified; omitted fields are left unchanged. Common updates include `name`, `description`, `external_id`, `custom_data`, `public_read`, `public_write`, `expires_in`, and a `reference_media_id` (with optional `reference_focus`) that designates a representative media item for the subject.

Visibility cannot be tightened: a subject that is already `public_read` or `public_write` cannot be reset to private. Setting `public_write` implies `public_read`. If a `reference_media_id` is supplied, it must reference a media item that exists.

The response is the updated subject record.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `subject_uid` | string | Unique identifier of the subject to update. |

**Request body:** [SubjectSchema](#schema-subjectschema)

**Errors:**

- `400` — request body fails validation, or the update attempts to make a public subject private.
- `401` — missing or invalid Authorization header.
- `404` — subject not found in the caller's tenant, or the supplied `reference_media_id` does not exist.

### `DELETE /1/subjects/{subject_uid}`

**Delete a subject**

Permanently delete a subject owned by the caller's tenant. The subject must not be in use anywhere in the platform:

- It must not be the input or output subject of any application in the tenant. Unbind it from all applications first.
- It must not be associated with any network camera in the tenant.
- It must not be a public subject (`public_read` or `public_write`). Public subjects cannot be deleted.

Returns `204 No Content` on success.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `subject_uid` | string | Unique identifier of the subject to delete. |

**Errors:**

- `400` — subject is public, or is bound to one or more applications as an input or output subject.
- `401` — missing or invalid Authorization header.
- `404` — subject not found in the caller's tenant.
- `412` — subject is linked to a network camera and cannot be deleted while that link exists.

### `GET /1/subjects/{subject_uid}`

**Retrieve a subject**

Return the subject identified by `subject_uid`, including its name, description, visibility flags, expiration policy, reference media, and a `consensus_summary` giving the current consensus counts by app data type.

A caller can fetch any subject owned by their tenant. Subjects owned by another tenant are visible only if they are publicly readable, publicly writeable, or have been explicitly shared with the caller's tenant. When the subject belongs to another tenant, the `created_by` field is omitted from the response.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `subject_uid` | string | Unique identifier of the subject to retrieve. |

**Response:** [SubjectSchema](#schema-subjectschema)

**Errors:**

- `401` — missing or invalid Authorization header.
- `404` — subject not found, or not visible to the caller's tenant.

### `POST /1/subjects/{subject_uid}/media`

**Associate media with a subject**

Authoritatively associate a media item with a subject. This is the primary mechanism for labeling media: it submits a user assertion that the subject is (or is not) present in the media item, optionally with a focus region and application-specific data.

The body identifies the media via `media_id` and may supply:

- `consensus` — `True`, `False`, `Sidelined`, or `None` (default). When set to one of the explicit values, this records authoritative user feedback. When `None`, the assertion is treated as a non-consensus observation and `uncal_prob` must be supplied to convey the raw confidence.
- `focus` — a focus region within the media: a bounding box (`{x0, y0, x1, y1}`, validated against the source media's dimensions), a polygon, or a mask (referenced by `area_mask_media_id`, supplied inline as a Base64-encoded PNG in `area_mask_png`, or as one or more run-length-encoded masks in `area_mask_rles`).
- `app_data_type` and `app_data` — application-specific payload describing detections, counts, segments, or masks. The supported `app_data_type` values depend on the application types enabled for the tenant. When supplied together with `consensus: True`, both fields must be set.
- `capture_tag` — an arbitrary caller-supplied tag attached to the assertion.
- `force_feedback`, `force_review`, `force_random_feedback` — flags that influence how the platform routes the media for downstream feedback collection.
- `enable_wait_result` — when `true`, prepares the assertion so a subsequent detections fetch can block until processing completes (used to convert this asynchronous call into a synchronous round-trip).

Cross-tenant writes are allowed when the subject is `public_write` or has been explicitly shared with write access.

The response contains a `capture_id` that uniquely identifies the submitted assertion and can be used to correlate with subsequent detection records.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `subject_uid` | string | Unique identifier of the subject to associate the media with. |

**Request body:** [SubjectMediaCapture](#schema-subjectmediacapture)

**Errors:**

- `400` — request body fails validation; `app_data` and `app_data_type` are not both supplied when `consensus` is `True`; `uncal_prob` is set when `consensus` is not `None`; `focus` box coordinates fall outside the source media's image dimensions or are otherwise invalid; an `area_mask_png` cannot be decoded or its MD5/parent media does not match the referenced `area_mask_media_id`; an `area_mask_rles` mask size does not match the source image dimensions; or `app_data` for `area_mask`/`area_mask_set` is missing all of `area_mask_media_id`, `area_mask_png`, and `area_mask_rles`.
- `401` — missing or invalid Authorization header.
- `404` — subject not found or not writeable by the caller's tenant; `media_id` not found; an `area_mask_media_id` referenced from `app_data` or `focus` does not exist.

### `GET /1/subjects/{subject_uid}/media`

**List media associated with a subject**

Return media items associated with a subject, paired with the corresponding subject-media association record. Supports time-range, probability-range, and consensus filtering, plus three sort orders.

Query parameters:

- `start`, `end` — Unix timestamp range to filter by; the field that this range applies to depends on `sort`.
- `duration` — alternative to `start`/`end`: returns the most recent window of the given duration in seconds.
- `probability_lower`, `probability_upper` — restrict results to the given association-probability range (`0.0`–`1.0`).
- `consensus` — `True`, `False`, `Sidelined`, or `None`. `True` returns associations the platform considers positive consensus (use as positive training examples), `False` returns negative consensus, `Sidelined` returns associations explicitly removed from training, `None` returns non-consensus associations. Omit the parameter to include all associations regardless of consensus.
- `sort` — `time` (default; orders by association update time), `probability`, or `media_timestamp`.
- `reverse` — `true` to invert the sort order.
- `cursor` — pagination cursor returned in `paging.next` of a prior response.
- `limit` — page size (1–1000, default 100).
- `abridged_media` — when `true`, each result's `media` object contains only `media_id` instead of the full media record.
- `enable_media_pre_count` — when `true`, the response includes a `media_count` reflecting the total number of associations matching the filter, computed in a bounded pre-query. If the pre-query times out (`media_pre_count_timeout`, default 15 seconds), `media_count` is returned partial and the HTTP status is `206 Partial Content`.

Each result item has the shape `{"media": <media item>, "subject": <subject-media association>}`. The subject-media association carries `media_id`, `subject_uid`, `probability` (current `[0, 1]` association probability), `updated_at` (last update timestamp), `consensus` (`True`, `False`, `Sidelined`, or `None`), and any application-specific `app_data_type`/`app_data` and `focus`. Pagination metadata is returned in `paging.next` as a fully-qualified URL.

If the subject belongs to another tenant, the response is permitted only when the subject is publicly readable or has been shared with the caller's tenant; the `created_by` fields are omitted in that case.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `subject_uid` | string | Unique identifier of the subject to query. |

**Query params:** [SubjectMediaSearch](#schema-subjectmediasearch)

**Response:** array of [SubjectMediaSearchResults](#schema-subjectmediasearchresults)

**Errors:**

- `400` — invalid query parameters (e.g. `start >= end`, `probability_lower >= probability_upper`).
- `401` — missing or invalid Authorization header.
- `404` — subject not found, or not readable by the caller's tenant.
- `206` — returned with the response body when `enable_media_pre_count=true` and the pre-count query did not finish within the configured timeout; `media_count` reflects a partial count.

### `DELETE /1/subjects/{subject_uid}/media`

**Remove a subject-media association**

Completely remove the association between a subject and a specific media item. The `media_id` is supplied as a query parameter; an optional `focus` query parameter (URL-encoded JSON) scopes the removal to a single focus region when multiple associations exist for the same `media_id`.

Returns `204 No Content` on success.

Cross-tenant deletes are allowed only when the subject is `public_write` or has been explicitly shared with write access.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `subject_uid` | string | Unique identifier of the subject. |

**Errors:**

- `400` — missing or invalid `media_id`.
- `401` — missing or invalid Authorization header.
- `404` — subject not found or not writeable by the caller's tenant.

### `GET /1/subjects/{subject_uid}/detections`

**Get the detection history for a subject-media association**

Return the full ordered list of detections — model predictions and user feedback assertions — that contributed to the current association between the subject and the media item identified by `media_id`.

Each entry carries a `detection_id`, the originating `user_id` (for user feedback) or `model_id` and `model_image_id` (for model predictions), the producing `app_id`, the `origin` (`edgeflow` or `cloudcore`), the raw uncalibrated probability `uncal_prob`, the previous probability `prev_prob`, the resulting consensus contribution, any `focus` region or `app_data`, and the `created_at` timestamp. This is the underlying audit trail behind the aggregate `probability` and `consensus` values returned by `GET /1/subjects/{subject_uid}/media`.

When the subject belongs to another tenant, the response is allowed only if the subject is publicly readable or has been shared with the caller's tenant; per-detection `created_by` / `tenant_id` fields are omitted in that case.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `subject_uid` | string | Unique identifier of the subject. |

**Query params:**

| Name | Type | Required | Description |
|---|---|---|---|
| `media_id` | string | **yes** | The media item whose detection history should be returned. |

**Response:** [SubjectDetectionSchema](#schema-subjectdetectionschema)

**Errors:**

- `400` — missing or invalid `media_id`.
- `401` — missing or invalid Authorization header.
- `404` — subject not found, or not readable by the caller's tenant.

### `GET /1/subjects/{subject_uid}/consensusHistory`

**Get a subject's consensus count history**

Return a time series of the subject's consensus counts. Each point is a snapshot in time of how many media items had consensus `True`, `False`, or `Sidelined` for the subject as of that timestamp, broken down by app data type when applicable. This is the data behind training-progress charts and answers "how has the size of this subject's positive/negative training set evolved over time?"

By default the endpoint returns the last 12 months of history. Use `start` and `end` (Unix timestamps) to widen or narrow the window, `limit` to cap the number of points returned, and `reverse=true` to receive points in descending time order. Supply `user_id` to scope the counts to consensus contributions originating from a specific user. If no records exist in the requested window, the most recent point preceding the window is returned so the caller has a non-empty baseline.

When the subject belongs to another tenant, the response is allowed only if the subject is publicly readable or has been shared with the caller's tenant.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `subject_uid` | string | Unique identifier of the subject. |

**Query params:** [ConsensusHistorySearch](#schema-consensushistorysearch)

**Response:** `{ "data": [ { "timestamp": <float>, "subjects": { "<subject_uid>": { "<consensus_type>": <count>, ... } } } ] }`

**Errors:**

- `401` — missing or invalid Authorization header.
- `404` — subject not found, or not readable by the caller's tenant.

### `POST /1/subjects/{subject_uid}/mediaDisassociate`

**Bulk-disassociate media from a subject**

Schedule the removal of a set of subject-media associations matching a filter or explicit list of media ids. Useful for cleaning up large numbers of associations (for example, expiring stale feedback for a long-lived input subject) without issuing one DELETE per media item.

The request body specifies the target set in one of two ways:

- A `filters` block selecting associations by time range (`start`, `end`, with `time_range_selector` choosing between `update_timestamp` and `media_timestamp`), `probability_lower`/`probability_upper`, and `consensus`. The optional `unselected_media_ids` list excludes specific media items from the filtered set.
- A non-empty `selected_media_ids` list naming the exact media items to disassociate. When `selected_media_ids` is non-empty, `filters` is ignored.

The request is accepted for asynchronous processing and returns a `subject_cleanup_request_id` that identifies the bulk operation. The actual disassociation runs in the background; query the subject's media list afterwards to confirm completion.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `subject_uid` | string | Unique identifier of the subject. |

**Request body:** [BulkSubjectMediaDisassociateRequestSchema](#schema-bulksubjectmediadisassociaterequestschema)

**Response:** `{ "message": { "subject_cleanup_request_id": "<id>" } }`

**Errors:**

- `400` — neither `filters` nor a non-empty `selected_media_ids` was supplied; request body fails validation.
- `401` — missing or invalid Authorization header.
- `404` — subject not found.

## Schemas

### `DetectionSchema` <a id='schema-detectionschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `assertion_prefix` | string \| null | no | default=None | Identifier prefix shared by detections belonging to the same submitted assertion. |
| `assertion_id` | string \| null | no | default=None | Unique identifier of this detection, returned as `detection_id`. |
| `user_id` | string \| null | no | default=None | Email of the user who produced this detection, for user feedback entries. |
| `model_id` | string \| null | no | default=None | Identifier of the model that produced this detection, for model predictions. |
| `model_image_id` | string \| null | no | default=None | Identifier of the specific model image (trained snapshot) that produced this detection. |
| `app_id` | string \| null | no | default=None | Identifier of the application that produced this detection. |
| `origin` | string \| null | no | default=None; one of {'edgeflow', 'cloudcore'} | Whether the detection was produced by an EdgeFlow appliance or by the cloud platform. |
| `uncal_prob` | number \| null | no | default=None; range(min=0, max=1) | Raw uncalibrated confidence reported by the user or model. |
| `created_at` | number \| null | no | default=None; range(min=0) | Unix timestamp at which the detection was recorded. |
| `prev_prob` | number \| null | no | default=None; range(min=0, max=1) | Aggregate subject-media association probability immediately before this detection was applied. |
| `activation` | string \| null | no |  | Optional activation marker associated with the detection. |
| `inference_focus` | any \| null | no |  | Focus region (box, polygon, or mask) reported by the inference engine for this detection. |

### `SubjectDetectionSchema` <a id='schema-subjectdetectionschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `subject_uid` | string | **yes** |  | The subject the detections are associated with. |
| `media_id` | string | **yes** |  | The media item the detections are associated with. |
| `detections` | [DetectionSchema](#schema-detectionschema) | **yes** |  | Ordered list of individual model predictions and user feedback entries contributing to this subject-media association. |

### `SubjectDetectionRequest` <a id='schema-subjectdetectionrequest'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `media_id` | string | **yes** |  | Media item whose detection history should be returned. |

### `SubjectMediaSchema` <a id='schema-subjectmediaschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `subject_uid` | string | **yes** |  | The subject in the association. |
| `media_id` | string | no |  | The media item in the association. |
| `app_data_type` | string \| null | no | default=None | Application-specific data type describing how `app_data` should be interpreted (for example `box`, `area_mask`, `area_mask_set`, `same`, `raw`). Must be a type enabled for the tenant. |
| `app_data` | any \| null | no | default=None | Application-specific payload (detections, counts, segments, masks). Its shape is determined by `app_data_type`. |
| `focus` | any \| null | no | default=None | Focus region (box, polygon, or mask) scoping this association to a sub-region of the media. |
| `consensus` | string \| null | no | default=None; one of {'True', 'False', 'Sidelined'} | Current consensus value for the association: `True` (positive consensus, used as a positive training example), `False` (negative consensus, used as a negative training example), or `Sidelined` (explicitly removed from training). |
| `result` | string \| null | no | default=None; one of {'True', 'False', 'Sidelined'} | Inbound-only alias for `consensus` accepted on requests. |
| `probability` | number | no | range(min=0, max=1) | Current calibrated probability in `[0, 1]` that the subject is associated with the media item. |
| `updated_at` | number | no | range(min=0) | Unix timestamp of the last update to this association. |

### `SubjectMediaCapture` <a id='schema-subjectmediacapture'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `media_id` | string | **yes** |  | Media item to associate with the subject. |
| `consensus` | string \| null | no | default='None'; one of {'True', 'False', 'Sidelined', 'None'} | Authoritative consensus value to record. Use `True`/`False`/`Sidelined` to submit user feedback; use `None` (the default) to submit a non-consensus observation and supply `uncal_prob`. |
| `capture_tag` | string | no | default=None | Optional caller-supplied tag attached to the assertion. |
| `force_feedback` | boolean | no | default=False | When `true`, force the associated media into the feedback queue regardless of routine selection logic. |
| `force_review` | boolean | no | default=False | When `true`, force the associated media into review regardless of routine selection logic. |
| `force_random_feedback` | boolean | no | default=False | When `true`, route the associated media to feedback via random selection. |
| `uncal_prob` | nullfloat | no | default=None | Raw uncalibrated confidence in `[0, 1]`. Must be set when `consensus` is `None` and must be omitted otherwise. |
| `enable_wait_result` | boolean | no | default=False | When `true`, prepares this assertion so a subsequent detections fetch can block until the assertion has been processed. |

### `SubjectMediaSearch` <a id='schema-subjectmediasearch'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `start` | number | no | range(min=0) | Lower bound of the time-range filter (Unix timestamp). The field this applies to depends on `sort`. |
| `end` | number | no | range(min=0) | Upper bound of the time-range filter (Unix timestamp). The field this applies to depends on `sort`. |
| `duration` | number | no | range(min=0) | Alternative to `start`/`end`: when supplied without an explicit range, returns the most recent window of this duration (seconds). |
| `probability_upper` | number | no | default=1.0; range(min=0, max=1) | Upper bound (inclusive) on the association probability. |
| `probability_lower` | number | no | default=0.0; range(min=0, max=1) | Lower bound (inclusive) on the association probability. |
| `limit` | integer | no | default=100; range(min=1, max=1000) | Maximum number of results to return in this page. |
| `reverse` | boolean | no | default=False | When `true`, return results in descending order of the sort key. |
| `cursor` | number | no | default=None; range(min=0) | Opaque pagination cursor; supply the value taken from `paging.next` of the prior response. |
| `consensus` | string \| null | no | default=None; one of {'True', 'False', 'Sidelined', 'None'} | Filter to associations with this consensus value; omit to include all consensus values. |
| `sort` | string | no | default='time'; one of {'time', 'probability', 'media_timestamp'} | Sort key: `time` orders by association update time, `probability` by association probability, `media_timestamp` by the underlying media item's timestamp. |
| `abridged_media` | boolean | no | default=False | When `true`, the `media` object in each result contains only `media_id` rather than the full media record. |
| `enable_media_pre_count` | boolean | no | default=False | When `true`, issue a pre-query to count the set of media matching the above search parameters. The count is returned as `media_count` in the response. |
| `media_pre_count_timeout` | integer | no | default=15 | Maximum number of seconds the pre-count query may run before returning a partial count and HTTP `206`. |

### `SubjectMediaSearchResults` <a id='schema-subjectmediasearchresults'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `media` | any | no |  | The media item associated with the subject (abridged to just `media_id` when `abridged_media=true`). |
| `media_list` | any \| null | no | default=None | All media items implicated by this association, including any peer media referenced by an `app_data_type` of `same`. |
| `other_media` | any \| null | no | default=None | Media items beyond the primary one — peer media referenced by an `app_data_type` of `same`. |
| `subject` | [SubjectMediaSchema](#schema-subjectmediaschema) | **yes** |  | The subject-media association record itself. |
| `focus` | any \| null | no | default=None | Focus region (box, polygon, or mask) for this association. |

### `BulkSubjectMediaDisassociateFilterSchema` <a id='schema-bulksubjectmediadisassociatefilterschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `time_range_selector` | string | **yes** | one of {'media_timestamp', 'update_timestamp'} | Which timestamp `start`/`end` apply to: the media item's own timestamp or the association's last-update timestamp. |
| `start` | number | no | range(min=0) | Lower bound of the time-range filter (Unix timestamp). |
| `end` | number | no | range(min=0) | Upper bound of the time-range filter (Unix timestamp). |
| `probability_upper` | number | no | default=1.0; range(min=0, max=1) | Upper bound (inclusive) on the association probability. |
| `probability_lower` | number | no | default=0.0; range(min=0, max=1) | Lower bound (inclusive) on the association probability. |
| `consensus` | string \| null | no | default=None; one of {'True', 'False', 'Sidelined', 'None'} | Restrict the operation to associations with this consensus value. |

### `BulkSubjectMediaDisassociateRequestSchema` <a id='schema-bulksubjectmediadisassociaterequestschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `filters` | [BulkSubjectMediaDisassociateFilterSchema](#schema-bulksubjectmediadisassociatefilterschema) \| null | no |  | Filter selecting the set of associations to remove. Ignored when `selected_media_ids` is non-empty. |
| `selected_media_ids` | list[string] \| null | no |  | Explicit list of media ids to disassociate. When non-empty, `filters` is ignored. |
| `unselected_media_ids` | list[string] \| null | no |  | Media ids to exclude from the set selected by `filters`. |

### `SubjectConsensus` <a id='schema-subjectconsensus'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `consensus` | string | **yes** |  | Consensus bucket the count applies to (`True`, `False`, or `Sidelined`). |
| `count` | integer | no | default=0 | Number of subject-media associations currently in this consensus bucket. |
| `app_data_type` | string | no |  | App data type the count is broken down by, when applicable. |

### `SubjectSchema` <a id='schema-subjectschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `subject_uid` | string | no |  | Unique identifier assigned by the platform when the subject is created. Read-only. |
| `name` | string | no |  | Short descriptive name for the subject. Required on create; up to 70 characters. |
| `description` | nullstring | no | default=None | Long-form description of what the subject represents and feedback instructions for users. |
| `external_id` | nullstring \| null | no | default=None | Caller-supplied identifier carried alongside the subject for cross-referencing with external systems. |
| `created_by` | string | no |  | Email of the user who created the subject. Read-only. |
| `tenant_id` | string | no |  | Tenant that owns the subject. Read-only. |
| `created_at` | number | no |  | Unix timestamp at which the subject was created. Read-only. |
| `modified_at` | number | no |  | Unix timestamp at which the subject was last modified. Read-only. |
| `public_read` | boolean | no |  | When `true`, the subject is readable by all tenants. |
| `public_write` | boolean | no |  | When `true`, all tenants may associate their own media with the subject. Implies `public_read`. |
| `expires_in` | nullfloat \| null | no | default=None; range(min=0) | Automatic expiration time for non-consensus subject-media associations, in months. Consensus associations are never auto-expired. Defaults to the tenant's configured value. |
| `consensus_summary` | [SubjectConsensus](#schema-subjectconsensus) | **yes** |  | Per-consensus-type counts of subject-media associations for this subject. Read-only. |
| `custom_data` | any \| null | no |  | Free-form caller-supplied metadata attached to the subject. |
| `reference_media_id` | string | no | default=None | Identifier of a representative media item for the subject (for example, used as a thumbnail). |
| `reference_focus` | any \| null | no | default=None | Focus region within `reference_media_id` that best represents the subject. |

### `ConsensusHistorySchema` <a id='schema-consensushistoryschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `timestamp` | number | **yes** |  | Unix timestamp of the history point (rounded to the nearest minute). |
| `count` | integer | **yes** |  | Number of subject-media associations in the consensus bucket at this point in time. |

### `ConsensusHistorySearch` <a id='schema-consensushistorysearch'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `user_id` | string | no | default=None | If supplied, scope the consensus history to contributions originating from a single user, rather than the aggregate across all users. |
| `start` | number | no | default=None | Lower bound of the history window (Unix timestamp). Defaults to one year before `end`. |
| `end` | number | no | default=None | Upper bound of the history window (Unix timestamp). Defaults to the current server time. |
| `limit` | integer | no | default=None | Maximum number of history points to return. |
| `reverse` | boolean | no | default=False | When `true`, return points in descending time order. |
