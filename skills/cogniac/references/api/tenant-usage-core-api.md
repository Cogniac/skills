# tenant-usage-core-api

Report per-tenant resource-usage metrics: media counts and bytes, model and feedback output counts, inference units consumed, active applications, and (for privileged callers) GPU training time. Used to drive billing visibility and dashboard charts.

All time fields — both the query window (`start`, `end`) and the record bounds (`start_time`, `end_time`) — are Unix epoch seconds.

Responses are wrapped as `{"data": [...], "paging": {...}}`. When the result set is paginated and more records remain in the requested window, `paging.next` is a fully-qualified URL that re-issues the query starting at the timestamp of the last returned record. Follow it until `paging.next` is absent.

## Endpoints

### `GET /1/usage/summary`

**get tenant usage summary**

Return a time-series of tenant-wide usage records covering the requested window. Each record summarizes activity for one bucket of size `period` (15-minute, hourly, daily, or monthly).

**Auth:** Bearer JWT required

**Query params:** see [GetUsageSchema](#schema-getusageschema).

**Response:** `{"data": [TenantUsageRecord, ...], "paging": {"next": "..."}}`. See [TenantUsageRecord](#schema-tenantusagerecord).

### `GET /1/usage/app/{app_id}`

**get app usage**

Return a time-series of usage records scoped to a single application. With `accumulate=true`, the response collapses the entire window into a single record whose counters are the sum across all buckets in the window.

The application must belong to the caller's tenant.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | Application id. Must belong to the caller's tenant. |

**Query params:** see [GetUsageSchema](#schema-getusageschema).

**Response:** `{"data": [AppUsageRecord, ...], "paging": {"next": "..."}}`. See [AppUsageRecord](#schema-appusagerecord). When `accumulate=true`, `data` contains at most one element and `paging.next` is omitted.

## Schemas

### `GetUsageSchema` <a id='schema-getusageschema'></a>

Query parameters accepted by both usage endpoints.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `start` | integer | **yes** |  | Window start, Unix epoch seconds. Must be strictly less than `end`. |
| `end` | integer | **yes** |  | Window end, Unix epoch seconds. |
| `period` | string | no | default='15min' | Bucket size for the returned time-series. One of `15min`, `hour`, `day`, `month`. Applies to `/1/usage/summary`. |
| `accumulate` | boolean | no | default=False | If true, collapse all records in the window into a single aggregated record. Applies to `/1/usage/app/{app_id}`. |
| `limit` | integer | no | default=None | Maximum number of records to return. Must be greater than zero when supplied. When omitted, the service chooses a default based on `period`. |

### `TenantUsageRecord` <a id='schema-tenantusagerecord'></a>

One tenant-wide usage bucket. Counter fields (`model_outputs`, `user_feedback`, `other_outputs`, `amu`, `gpu_training_seconds`) are sums over the bucket interval. Gauge fields (`media_count`, `media_bytes`) reflect the value at the bucket's `end_time`.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `tenant_id` | string | no |  | Tenant the record belongs to. |
| `start_time` | integer | no |  | Bucket start, Unix epoch seconds. |
| `end_time` | integer | no |  | Bucket end, Unix epoch seconds. |
| `model_outputs` | integer | no |  | Count of model-generated detections produced in the bucket. |
| `user_feedback` | integer | no |  | Count of user-supplied feedback events recorded in the bucket. |
| `other_outputs` | integer | no |  | Count of non-model, non-feedback detection outputs produced in the bucket (e.g. rule-based or integration-app outputs). |
| `media_count` | integer | no |  | Total media items stored for the tenant as of `end_time`. |
| `media_bytes` | integer | no |  | Total bytes of media stored for the tenant as of `end_time`. |
| `amu` | integer | no |  | Active Media Units consumed in the bucket — Cogniac's normalized unit of inference work. |
| `mpix_per_amu` | integer | no |  | Megapixels processed per AMU for the bucket. |
| `active_apps` | list[string] | no |  | Application ids that produced any activity in the bucket. |
| `active_model_apps` | list[string] | no |  | Subset of `active_apps` whose activity included model inference. |
| `gpu_training_seconds` | integer | no |  | GPU-seconds spent training models for this tenant in the bucket. Returned only to callers with `cogniac_admin` or `cogniac_support` roles. |

### `AppUsageRecord` <a id='schema-appusagerecord'></a>

One per-application usage bucket. With `accumulate=true`, the single returned record's counters are summed across the entire requested window and its `end_time` is the timestamp of the last bucket.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `tenant_id` | string | no |  | Tenant the application belongs to. |
| `app_id` | string | no |  | Application id. |
| `start_time` | integer | no |  | Bucket start, Unix epoch seconds. |
| `end_time` | integer | no |  | Bucket end, Unix epoch seconds. |
| `model_outputs` | integer | no | default=0 | Count of model-generated detections produced by this application in the bucket. |
| `user_feedback` | integer | no | default=0 | Count of user-supplied feedback events for this application in the bucket. |
| `other_outputs` | integer | no | default=0 | Count of non-model, non-feedback outputs produced by this application in the bucket. |
| `amu` | integer | no | default=0 | Active Media Units consumed by this application in the bucket. |
| `gpu_training_seconds` | integer | no |  | GPU-seconds spent training models for this application in the bucket. Returned only to callers with `cogniac_admin` or `cogniac_support` roles. |
