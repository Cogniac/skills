# app-replay-service-v2

Replay submits previously captured media back through an application's processing pipeline so the application can re-evaluate it under updated models, updated configuration, or with explicit feedback collection. A replay is bounded by the subjects (or single media item) the caller selects, plus optional filters on probability range, update timestamp, ordering, and OCR text.

Replays are tracked as long-running, asynchronous jobs. Starting a replay returns a `replay_id` and an initial `in-progress` status; callers then poll the status endpoints to observe `processed`, `selected`, `replayed`, `filtered`, and `skipped` counters until the replay reaches `success` or `failure`. Replays can be stopped at any time before completion.

All endpoints are scoped to V21 applications under the caller's tenant. The caller must have authorization to read both the target application and any subject whose media is being replayed; subjects owned by another tenant are eligible only when they are explicitly shared with the caller's tenant or marked publicly readable.

## Endpoints

### `POST /21/applications/{app_ids}/replay`

**Start a replay**

Initiates a new replay for one or more applications and returns a record describing the queued replay. Exactly one of `replay_subjects` or `replay_media` must be supplied in the request body: pass `replay_subjects` to replay a bounded selection of subject-media (optionally narrowed by probability range, time range, replay order, OCR filter, validation-set-only, and per-subject `limit`), or pass `replay_media` to replay a single media item (optionally with `foci`). When `replay_media` is used and `force_feedback` is not explicitly set, it defaults to `true`.

The same replay specification can be applied to several applications at once by passing a comma-separated list of application IDs in the path; this is intended for cases where the same media should be re-evaluated by multiple apps in a single call. Each application receives its own `replay_id`. The response is a single record when a single application is given and a list of records, one per application, when multiple are given.

Replays run asynchronously. Poll `GET /21/applications/{app_id}/replay/{replay_id}` to observe progress; call `DELETE /21/applications/{app_id}/replay/{replay_id}` to stop a replay before it completes.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_ids` | string | comma-separated list of application IDs. Normally it will contain a single app_id, but for efficiency of replay a list of apps is supported. |

**Request body:** [ReplayArgumentsSchema](#schema-replayargumentsschema)

**Response:** [ReplayTableSchema](#schema-replaytableschema) — data if app_ids contains a single item else a list of that data, one per app_id

**Errors:**

| Status | Condition |
|---|---|
| 400 | Neither `replay_subjects` nor `replay_media` is supplied, or both are supplied, or either is supplied but empty. |
| 400 | `replay_filters` contains an entry with an unrecognized `filter` value, or `time_lower` is not strictly less than `time_upper`, or any field fails Marshmallow validation (e.g., `probability_upper`/`probability_lower` outside `[0, 1]`, `limit` negative, `replay_order` not one of the allowed values). |
| 404 | One of the supplied applications does not exist in the caller's tenant, or exists but is not active. |
| 404 | `replay_media` refers to a media item that does not exist or does not belong to the caller's tenant. |
| 404 | One or more entries in `replay_subjects` belong to another tenant and are neither shared with the caller's tenant nor publicly readable. |

### `GET /21/applications/{app_id}/replay/active`

**List active replays for an application**

Returns the set of replays for the given application that are still active (i.e., `active = 1`). Use this to find replays that are either in progress or that have not yet been stopped. The response is a list, ordered by the service; an empty list means there are no active replays.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | Application ID to query. |

**Response:** [ReplayTableSchema](#schema-replaytableschema) — list of items which have active=1

### `GET /21/applications/{app_id}/replay`

**List recent replays for an application**

Returns the most recent replays for the given application, up to 100 entries, in reverse chronological order (newest first). Includes both active and completed replays. Use this for a recent-history view; use `GET .../replay/active` to filter to only in-flight replays, or `GET .../replay/{replay_id}` to retrieve a specific replay.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | Application ID to query. |

**Response:** [ReplayTableSchema](#schema-replaytableschema) — list of up to 100 most recent replays

### `GET /21/applications/{app_id}/replay/{replay_id}`

**Get replay status**

Returns the current record for a single replay, including its arguments, status counters, active flag, and creation timestamp. Use this to poll an in-progress replay; the `replay_status.status` field transitions from `in-progress` to either `success` or `failure`, and the counters (`processed`, `filtered`, `selected`, `replayed`, `skipped`) update as work progresses.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | Application ID the replay belongs to. |
| `replay_id` | string | Identifier returned when the replay was started. |

**Response:** [ReplayTableSchema](#schema-replaytableschema)

**Errors:**

| Status | Condition |
|---|---|
| 404 | No replay with the given `replay_id` exists for the given `app_id`. |

### `DELETE /21/applications/{app_id}/replay/{replay_id}`

**Stop a replay**

Requests that an in-progress replay stop. If the replay is currently active, it is marked inactive (`active = 0`), its status is set to `failure` with the failure message `"Replay stopped by the user."`, and the replay will halt at its next checkpoint. If the replay is already complete or already stopped, the call is a no-op. Returns 200 in either case.

Stopping a replay does not roll back media that has already been re-evaluated by the application; it only prevents further work for that `replay_id`.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | Application ID the replay belongs to. |
| `replay_id` | string | Identifier of the replay to stop. |

**Errors:**

| Status | Condition |
|---|---|
| 404 | No replay with the given `replay_id` exists for the given `app_id`. |

## Schemas

### `OcrReplayFilterSchema` <a id='schema-ocrreplayfilterschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `filter` | string | **yes** | one of {'ocr'} | Filter type discriminator; must be `"ocr"` to select OCR-based filtering. |
| `ocr_string` | string | **yes** |  | OCR text that media must match to be included in the replay. |

### `ReplayArgumentsSchema` <a id='schema-replayargumentsschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `replay_subjects` | list[string] \| null | no |  | list of subject_uid's to replay (must be readable by the tenant) |
| `replay_media` | string \| null | no |  | media_id to replay (one fo replay_subjects or replay_media must be specified, both are not allowed) |
| `foci` | list[any] \| null | no | default=None | List of focus dicts (only for replaying individual media w/ focus) |
| `validation_only` | boolean | no | default=False | replay from a validation set only |
| `replay_order` | string \| null | no | default='first'; one of {'first', 'last', 'random', 'highest_probability', 'lowest_probability'} | determines which order to replay |
| `probability_upper` | number \| null | no | default=1.0; range(min=0, max=1) | upper limit of subject-media probability to replay |
| `probability_lower` | number \| null | no | default=0.0; range(min=0, max=1) | lower limit of subject-media probability to replay |
| `time_upper` | number \| null | no | default=None; range(min=0) | upper limit of subject-media update timestamp to replay |
| `time_lower` | number \| null | no | default=None; range(min=0) | lower limit of subject-media update timestamp to replay |
| `limit` | number \| null | no | default=1000; range(min=0) | max media items per subject to replay |
| `force_feedback` | boolean \| null | no | default=False | force feedback on all replayed media |
| `replay_filters` | list[any] | no |  | filters the raw data in a request comes as: "replay_filters": [{"filter": "ocr", "ocr_string": str}] |

### `ReplayStatusSchema` <a id='schema-replaystatusschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `status` | string | no | one of {'failure', 'success', 'in-progress'} | Current state of the replay: `in-progress` while work remains, `success` when all selected media have been replayed, `failure` if the replay errored or was stopped. |
| `failure_message` | string \| null | no |  | Human-readable description of why the replay failed; populated only when `status` is `failure`. |
| `processed` | integer | no | default=0; range(min=0) | Count of subject-media records examined so far. |
| `filtered` | integer | no | default=0; range(min=0) | Count of records excluded by the supplied filters (probability range, time range, OCR filter, etc.). |
| `selected` | integer | no | default=0; range(min=0) | Count of records that passed filtering and were selected for replay. |
| `replayed` | integer | no | default=0; range(min=0) | Count of records successfully resubmitted to the application pipeline. |
| `skipped` | integer | no | default=0; range(min=0) | Count of selected records that were not replayed (e.g., already in flight or ineligible at replay time). |

### `ReplayTableSchema` <a id='schema-replaytableschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `app_id` | string | no |  | Application this replay belongs to. |
| `replay_id` | string | no |  | Unique identifier for the replay, assigned when the replay is started. |
| `active` | integer | no | range(min=0, max=1) | `1` while the replay is running, `0` once it has completed or been stopped. |
| `replay_arguments` | [ReplayArgumentsSchema](#schema-replayargumentsschema) | no |  | The arguments the replay was started with, echoed back for reference. |
| `replay_status` | [ReplayStatusSchema](#schema-replaystatusschema) | no |  | Current status and progress counters for the replay. |
| `user_id` | string \| null | no |  | Email of the user who initiated the replay. |
| `created_at` | number | no |  | Unix timestamp (seconds) at which the replay was started. |
