# ops-review-core-api

Operator-review queue for verifying or overriding Cogniac application predictions on the factory floor. Manufacturing operators (and upstream EdgeFlow workflows) post media — typically tagged with the application's predicted detections — to a pending review queue; the operator opens each item in the review UI, agrees with or corrects the prediction, and submits a result. Submitted results land in a separate, searchable results store that downstream systems (MES, audit, reporting) can poll.

A review queue entry (`OpsReview`) groups one or more media items under a single `review_id`. Each item may carry the application's detections so the operator can see what the model proposed. Once the operator submits a `result` for the `review_id`, the item moves out of the pending queue and into the results store, stamped with the reviewer's identity and any operator comment.

All endpoints require Bearer JWT authentication and operate against the caller's tenant.

## Endpoints

### `POST /1/ops/review`

**Add an item to the operations review queue**

Enqueue a new review item for a manufacturing operator to inspect. The request body is an [OpsReviewSchema](#schema-opsreviewschema) carrying one or more `review_items`, each identifying a media item (by `media_id` or `external_media_id`) and optionally the detections that the application produced for it. An optional `review_unit` lets the caller tag the entry with a customer-defined identifier (for example, a production line, station, or work order) so results can later be searched per unit. An optional `source` tags the entry with a free-form origin label that supports source-scoped queries.

If a `review_items` entry supplies only `external_media_id`, the service resolves it to the tenant's matching `media_id` before enqueueing. Submissions from an EdgeFlow upload that has not yet finished registering the media may be briefly retried during resolution; if no matching media is found, the request fails.

On success the response carries the newly assigned `review_id` plus the stored review record.

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_billing, tenant_ops, tenant_user}`

**Request body** (`application/json`): [OpsReviewSchema](#schema-opsreviewschema)

### `GET /1/ops/review`

**Get the most recent pending review**

Return the single most recent pending review entry in the caller's tenant. Intended for lightweight polling clients that consume the queue one item at a time. If no pending entry exists, the response is empty. Use `GET /1/ops/reviews` for paged retrieval of multiple entries.

**Auth:** Bearer JWT required

### `GET /1/ops/reviews`

**List pending review entries**

List pending review entries in the caller's tenant, ordered by creation time. Results may be filtered by time range and optionally restricted to a single `source`. Newest-first by default; pass `reverse=false` for oldest-first. Pagination is cursor-based — the response carries a `paging.next` URL when more entries are available; pass it through to retrieve the following page.

Entries whose underlying media has been deleted are filtered out of the response (and pruned from the queue) automatically.

**Auth:** Bearer JWT required

**Query params:** [GetMultiOpsReviewSchema](#schema-getmultiopsreviewschema)

### `GET /1/ops/review/pending`

**Count pending review entries**

Return the count of pending review entries for the caller's tenant. Pass `source` to count only entries tagged with that source.

**Auth:** Bearer JWT required

**Query params:**

| Name | Type | Description |
|---|---|---|
| `source` | string | Restrict the count to entries tagged with this source label. |

**Response:**

```json
{"pending": 42}
```

### `POST /1/ops/results`

**Submit an operator review result**

Record the operator's verdict for a review entry. The pending entry identified by `review_id` is moved out of the queue and into the results store, stamped with the submitting user's identity, the current timestamp, and the supplied `result` string (and optional `comment`).

The `result` value is a free-form, customer-defined string — typical values represent the operator's decision (for example a pass/fail label or a corrected subject identifier). The special value `Missed Defect` is reserved for operator-initiated reports that do not correspond to a pre-existing queue entry; in that mode the caller supplies a fresh `review_id` and the service creates the result record directly without requiring a matching pending entry.

If the supplied `review_id` does not match a pending entry, the service checks the results store for a prior result against the same id; if one exists it is replaced (idempotent re-submission). Otherwise the request fails.

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_billing, tenant_ops, tenant_user}`

**Form / query params:**

| Name | Type | Required | Description |
|---|---|---|---|
| `review_id` | string | **yes** | Identifier of the pending review entry to resolve. |
| `result` | string | **yes** | Operator's verdict. |
| `comment` | string | no | Free-form operator note. |
| `source` | string | no | Source label, used when creating a user-initiated report (e.g. `Missed Defect`). |

### `GET /1/ops/results`

**Search submitted review results**

Search the results store for entries that an operator has already resolved. Results may be filtered by time range, `source`, `result` value, `review_unit`, `media_id`, or `external_media_id`. Newest-first ordering is opt-in via `reverse=true`; default ordering is oldest-first.

Time-range queries are cursor-paged the same way as `/1/ops/reviews`. Queries that filter by `media_id`, `external_media_id`, or `review_unit` return the full matching set without paging — apply `limit` to cap the result count.

**Auth:** Bearer JWT required

**Query params:** [SearchOpsReviewSchema](#schema-searchopsreviewschema)

### `DELETE /1/ops/review/{review_id}`

**Delete a review entry**

Remove the review entry identified by `review_id`. If the entry is still pending, it is removed from the pending queue; if a result has already been submitted, the corresponding result record is removed instead.

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_billing, tenant_ops, tenant_user}`

**Path params:**

| Name | Type | Description |
|---|---|---|
| `review_id` | string | Identifier of the review entry to delete. |

Returns `204 No Content` on success.

## Schemas

### `_ReviewDetection` <a id='schema-_reviewdetection'></a>

A single application detection presented to the operator alongside the media.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `subject_uid` | string | no |  | Identifier of the subject the application detected. |
| `probability` | number | no |  | Model confidence for the detection. |
| `app_data_type` | string | no |  | Discriminator describing the shape of `app_data` (for example a bounding box or other geometry payload). |
| `app_data` | any | no |  | Type-specific detection payload (geometry, scores, or other application output). |

### `_ReviewItemSchema` <a id='schema-_reviewitemschema'></a>

A single media item enqueued for operator review. Supply `media_id` directly, or `external_media_id` and let the service resolve it against the tenant's media library.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `media_id` | string | no |  | Cogniac media identifier. |
| `external_media_id` | string | no |  | Customer-supplied media identifier; resolved to `media_id` on submission. |
| `detections` | list[[_ReviewDetection](#schema-_reviewdetection)] | no |  | Application detections to display alongside the media. |

### `OpsReviewSchema` <a id='schema-opsreviewschema'></a>

A review queue entry. The same shape is returned for both pending entries and submitted results; `result`, `result_by`, and reviewer-supplied `comment` are populated only after an operator has submitted a verdict.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `review_id` | string | no |  | Server-assigned identifier for the review entry. |
| `review_unit` | string | no |  | Customer-defined grouping label (for example a production line, station, or work order). |
| `created_at` | number | no |  | Unix timestamp at which the entry was created or, for submitted results, at which the result was recorded. |
| `created_by` | string | no |  | Identity of the user or system that enqueued the entry. |
| `result` | string | no |  | Operator verdict; populated after a result is submitted. |
| `result_by` | string | no |  | Identity of the operator who submitted the result. |
| `review_items` | list[[_ReviewItemSchema](#schema-_reviewitemschema)] | **yes** |  | Media items, with their predicted detections, that comprise this review entry. |
| `comment` | string | no |  | Free-form operator note attached at result submission. |
| `source` | string | no |  | Free-form origin label assigned by the caller; supports source-scoped queries. |

### `GetMultiOpsReviewSchema` <a id='schema-getmultiopsreviewschema'></a>

Query parameters for listing pending review entries.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `start` | number | no |  | Lower bound (Unix timestamp) on entry creation time. |
| `end` | number | no |  | Upper bound (Unix timestamp) on entry creation time. |
| `reverse` | boolean | no | default=True | If true (default), order newest-first; otherwise oldest-first. |
| `limit` | integer | no | default=100 | Maximum entries to return per page. |
| `source` | string | no |  | Restrict results to entries tagged with this source label. |
| `cursor` | number | no | default=None | cursor value for paging, supplied by api |

### `SearchOpsReviewSchema` <a id='schema-searchopsreviewschema'></a>

Query parameters for searching submitted review results.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `review_unit` | string | no |  | Restrict to results tagged with this customer-defined unit. |
| `tenant_id` | string | no |  | Ignored; results are always scoped to the caller's tenant. |
| `start` | number | no |  | Lower bound (Unix timestamp) on result creation time. |
| `end` | number | no |  | Upper bound (Unix timestamp) on result creation time. |
| `reverse` | boolean | no | default=False | If true, order newest-first; default is oldest-first. |
| `limit` | integer | no | default=100 | Maximum entries to return. |
| `media_id` | string | no |  | Restrict to results whose `review_items` include this media id. |
| `result` | string | no |  | Restrict to results matching this verdict value. |
| `source` | string | no |  | Restrict to results tagged with this source label. |
| `external_media_id` | string | no |  | Restrict to results whose `review_items` include this external media id. |
| `cursor` | number | no | default=None | cursor value for paging, supplied by api |
