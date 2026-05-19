# application-core-api

The Application API manages Cogniac applications — the unit of computer-vision processing in the platform. An application consumes media from one or more input subjects, processes it (through a trained model or other configured logic), and emits detections to output subjects. Each application has an `application_type` that determines its behavior (classification, detection, OCR, point/box detection, network camera capture, integrations, and so on). The set of available types is fixed per tenant and can be inspected via the application-types endpoints.

Endpoints fall into a few groups: lifecycle (create, retrieve, update, delete, copy, donate model); inspection of model state and packaged model downloads; performance metrics (release-time, current-validation, and random test datasets) plus per-prediction model performance; runtime introspection (pending detections backlog, feedback backlog, application events, consensus history); and operational controls (replay and Meraki model export for tenants with that integration enabled).

All requests require a tenant-scoped bearer JWT obtained via the token endpoint, except the application-type listing endpoints, which accept either a tenant-scoped or basic token. Mutating endpoints on a specific application require that the caller be listed in the application's `app_managers` list, or hold the `tenant_admin` role; lighter-weight read endpoints accept any tenant member. Error responses follow the Cogniac convention: `4xx` for client errors (with a JSON `message` describing the failure) and `5xx` for server errors. Where an endpoint resolves an application by `app_id`, a missing or cross-tenant `app_id` returns `404 Application not found.`

## Endpoints

### `GET /1/applications/all/types/{application_type}`

**Retrieve an application type definition**

**Auth:** Bearer JWT required

Return the definition for a single application type, including its display name, description, whether it is model-based, the set of valid release metrics, supported execution targets (CloudCore, EdgeFlow, CloudFlow), supported input/output subject counts, and any app-data-type or focus configuration. Call this before creating or updating an application to discover which fields and configuration options the type supports.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `application_type` | string | The application-type identifier (for example `classification`, `box_detection`, `ocr`, `point_count_detection`). |

**Response:** [ApplicationTypeSchema](#schema-applicationtypeschema)

**Errors:**

| Status | Condition |
|---|---|
| 403 | The caller has neither a tenant token nor `cogniac_admin`/`cogniac_support`. |
| 404 | The requested application type does not exist. |

### `POST /1/applications`

**Create an application**

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_ops, tenant_user}`

Create a new application in the caller's tenant. The request body must include `type` (the `application_type`) along with any fields required by that type. The type definition (see `GET /1/applications/all/types/{application_type}`) determines which fields are accepted and which are required; type-specific configuration is supplied under `app_type_config`. The newly created application's `application_id` is returned in the response.

If the request body contains `source_application_id`, the endpoint instead initiates a copy of the referenced application — output subjects, model state, and evaluation metric configuration are duplicated into a new application. Copies are restricted to model-based application types. The copy is performed asynchronously: the response is `202 Accepted` with `{"application_id": "..."}` and the new application becomes usable once its creation completes.

For model-based types, output subjects supplied in the request must already exist in the tenant. Where the type defines a default detection threshold, one is applied for each output subject. Some types (such as `box_detection`, `kafka_client`, and `meraki_camera_capture`) have additional validation; for `meraki_camera_capture` the tenant must have the Meraki integration enabled and remain compliant with camera licensing.

**Request body:** application object (see [ApplicationTypeSchema](#schema-applicationtypeschema) for the type definition that governs accepted fields). When copying, supply [CopyApplicationRequestSchema](#schema-copyapplicationrequestschema).

**Errors:**

| Status | Condition |
|---|---|
| 400 | Missing or invalid `type`; copy of a non-model-based application requested; invalid output subjects; `subject_weights` supplied for a type that does not support it; invalid `box_detection` configuration; other application-input validation failures. |
| 404 | The referenced `source_application_id` does not exist in the tenant (copy flow). |
| 409 | Output-only application supplied with input subjects (returned by the update path; see also `POST /1/applications/{app_id}`). |

### `POST /1/applications/{app_id}`

**Update an application**

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_ops, tenant_user}`

Apply a partial update to an existing application. Only fields supplied in the request body are modified; omitted fields are left unchanged. The application type cannot be changed after creation. For model-based applications, output subjects cannot be modified after creation — to change them, create a new application.

Only users listed in the application's `app_managers` or holding the `tenant_admin` role may modify configuration. `app_managers` itself cannot be emptied (the application must always have at least one manager). Detection thresholds must lie in `[0, 1]`; `subject_weights` (only valid on `point_count_detection` applications) must be strictly positive.

For network-camera and camera-capture applications, output subjects are derived from associated cameras and cannot be edited directly; adding or removing a camera causes the camera's associated output subject to be added or removed accordingly. For `meraki_camera_capture` applications, camera additions are subject to license-compliance checks against the tenant's Meraki integration.

Returns the updated application object.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Errors:**

| Status | Condition |
|---|---|
| 400 | Caller is not an application manager; attempted change to output subjects of a model-based application; `app_managers` would be emptied; invalid `subject_weights`/`detection_thresholds`; input subject is also an output subject; other type-specific validation failure. |
| 403 | Caller's tenant does not match the application's tenant. |
| 404 | Application not found in the caller's tenant. |
| 409 | An output-only application is supplied with input subjects. |

### `DELETE /1/applications/{app_id}`

**Delete an application**

**Auth:** Bearer JWT; required roles: `{cogniac_support, tenant_admin, tenant_ops, tenant_user}`

Delete the application. Deletion removes the application configuration, severs its input/output subject associations, and disables further processing. For applications with integrations (`meraki_camera_capture`, `box_detection`), the corresponding integration resources are cleaned up. The application's history (events, performance metrics) may be retained for audit purposes.

Returns an empty body with status `204` on success.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Errors:**

| Status | Condition |
|---|---|
| 400 | Internal cleanup failed. |
| 404 | Application not found in the caller's tenant. |

### `GET /1/applications/{app_id}`

**Retrieve an application**

**Auth:** Bearer JWT required

Return the full application object, including configuration, current model state (when applicable), output subjects, app managers, training summary, and pending input count. Pass `?config_only=true` to obtain only configuration fields, omitting computed and model-derived fields; this is faster and is appropriate when only the application definition is required.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Query params:**

| Name | Type | Description |
|---|---|---|
| `config_only` | boolean | If `true`, omit model state, training summary, and queued media count. Defaults to `false`. |

**Errors:**

| Status | Condition |
|---|---|
| 403 | Caller's tenant does not match the application's tenant. |
| 404 | Application not found in the caller's tenant. |

### `GET /1/applications/{app_id}/detections`

**List application detections**

**Auth:** Bearer JWT required

Return detections produced by this application, sorted by time. Each result is a media item with a list of per-subject assertions made by the application's model and/or by users providing feedback. Use the `cursor` returned in `paging.next` to page through results.

By default, for model-based applications the response includes only model detections (`only_model` defaults to `true` when neither `only_user` nor `only_model` is supplied). For non-model-based application types both flags are ignored and all detections are returned.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Query params:**

| Name | Type | Description |
|---|---|---|
| `start` | number | Minimum update timestamp (Unix seconds). |
| `end` | number | Maximum update timestamp (Unix seconds). |
| `limit` | integer | Maximum number of results to return. |
| `reverse` | boolean | If `true`, sort descending by time. Defaults to `false`. |
| `only_user` | boolean | If `true`, return only user-supplied detections. |
| `only_model` | boolean | If `true`, return only model-supplied detections. |
| `probability_lower` | number | Lower bound of uncalibrated assertion probability `[0, 1]`. Defaults to `0`. |
| `probability_upper` | number | Upper bound of uncalibrated assertion probability `[0, 1]`. Defaults to `1`. |
| `consensus` | string | One of `True`, `False`, `Sidelined`, or `None`. Filter by consensus value. Defaults to returning all detections regardless of consensus. |
| `cursor` | number | Pagination cursor returned by a prior call. |

**Response:** `{"data": [<AppMediaDetectionSchema>...], "paging": {"next": "<url>"}}`. Each entry contains `media_id`, optional `focus`, `timestamp`, and a list of detection assertions. See [DetectionSchema](#schema-detectionschema).

**Errors:**

| Status | Condition |
|---|---|
| 404 | Application not found in the caller's tenant. |

### `POST /1/applications/{target_app_id}/donateModel`

**Donate a model from another application**

**Auth:** Bearer JWT; required roles: `{tenant_admin}` (caller may alternatively be listed as an app manager on the target application)

Asynchronously transfer the currently released model from a source application to a target application. Both applications must belong to the caller's tenant and be of the same model-based application type. Model donation is useful when starting a new application from a known-good model trained on a similar dataset.

Returns `202 Accepted` with an empty body once the donation has been queued. The model will become available on the target application once processing completes.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `target_app_id` | string | The application receiving the donated model. |

**Request body:** [DonateApplicationModelRequestSchema](#schema-donateapplicationmodelrequestschema)

**Errors:**

| Status | Condition |
|---|---|
| 400 | Source application not found; source and target are of different types; source application type is not model-based. |
| 403 | Caller is not an application manager of the target and is not a `tenant_admin`. |
| 404 | Target application not found. |

### `GET /1/applications/{id}/detections/pending`

**Get pending-detection count**

**Auth:** Bearer JWT required

Return the number of media items queued for inference but not yet processed by this application. Useful for operational visibility into application backlogs and for batch-processing flows that need to know when work is complete.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | The application identifier. |

**Response:** `{"pending": <integer or null>}`. `null` indicates the application's input queue could not be located.

**Errors:**

| Status | Condition |
|---|---|
| 404 | Application not found in the caller's tenant. |

### `POST /1/applications/{app_id}/classify`

**Classify a single image synchronously**

**Auth:** Bearer JWT required

Synchronously submit a single image file to this application's model and return the resulting detection. The image is supplied as a `multipart/form-data` file upload. The image is registered as a media item in the tenant (so repeated submissions of the same image are deduplicated by content hash) and dispatched to the application's inference path; the response returns the resulting detection assertions.

Only one file may be uploaded per request. This endpoint is appropriate for ad-hoc inference; for high-throughput workflows, submit media via the media API and consume detections via subjects.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Errors:**

| Status | Condition |
|---|---|
| 400 | No file supplied; timeout creating new media; failure dispatching the inference request. |
| 411 | More than one file uploaded. |

### `GET /1/applications/{app_id}/ccp`

**Retrieve the current released model summary (deprecated)**

**Auth:** Bearer JWT required

Return the currently released model for this application, including the model identifier, a download URL for the model package, and aggregate statistics (number of candidates, number of releases, last release time, output subjects). This endpoint is retained for backward compatibility; new integrations should prefer `GET /1/applications/{app_id}/models`.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Response:** [CCPSchema](#schema-ccpschema)

**Errors:**

| Status | Condition |
|---|---|
| 404 | Application not found, or no released model exists for this application. |

### `GET /1/applications/{app_id}/ccppkg`

**Download a released model package**

**Auth:** Bearer JWT required

Download the binary model package whose filename is supplied in the `ccp_filename` query parameter. The response is the raw package bytes; the `Range` header is honored, so partial downloads and resume are supported. The filename to use is returned in the `best_model_ccp_filename` field of `GET /1/applications/{app_id}/ccp`.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Query params:**

| Name | Type | Description |
|---|---|---|
| `ccp_filename` | string | The model package filename (required). |

**Errors:**

| Status | Condition |
|---|---|
| 400 | Caller is not authorized for this tenant's package downloads. |
| 403 | Tenant context missing from the token. |
| 404 | Application not found, or the requested package is unavailable. |

### `GET /1/applications/{app_id}/models`

**List released models**

**Auth:** Bearer JWT required

Return the released models for this application together with the most-recent leaderboard models (those that have not yet been released). Results are paged by release time using a cursor returned in `paging.next`.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Query params:** [ModelsSearch](#schema-modelssearch)

**Response:** `{"data": [<ModelsSchema>...], "paging": {"next": "<url>"}}`. See [ModelsSchema](#schema-modelsschema).

**Errors:**

| Status | Condition |
|---|---|
| 404 | Application not found in the caller's tenant. |

### `GET /1/applications/{app_id}/performance/releaseValidation`

**Get performance at model release time**

**Auth:** Bearer JWT required

Return the validation-set performance metrics for each model release, as measured at the moment the model was released. Returned metrics include accuracy, F1, precision, recall, and confusion-matrix counts (TP, FP, TN, FN), reported overall and per output subject, together with the data-set size and loss value at release time. Use this to track how the application's released models have performed historically against the data they were trained against.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Query params:** [PerformanceSearchSchema](#schema-performancesearchschema)

**Response:** `{"data": [<ApplicationPerformanceSchema>...]}`. See [ApplicationPerformanceSchema](#schema-applicationperformanceschema).

**Errors:**

| Status | Condition |
|---|---|
| 400 | `duration` is non-positive. |
| 404 | Application not found in the caller's tenant. |
| 409 | `start` greater than `end`. |

### `GET /1/applications/{app_id}/performance/currentValidation`

**Get all released models re-evaluated against the current validation set**

**Auth:** Bearer JWT required

Return performance metrics for all previously released models, re-evaluated against the application's current validation dataset. Use this to compare the performance of every released model on today's data, rather than the data each model was originally evaluated against.

If the application's configuration has been reset (its output subjects or type changed), historical models that were trained against the previous configuration are not re-evaluated and will not appear in the response.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Query params:** [PerformanceSearchSchema](#schema-performancesearchschema). `start`/`end` filter by original model release time; `duration` searches backwards from the present.

**Response:** `{"data": [<ApplicationPerformanceSchema>...]}`. See [ApplicationPerformanceSchema](#schema-applicationperformanceschema).

**Errors:**

| Status | Condition |
|---|---|
| 400 | `duration` is non-positive. |
| 404 | Application not found in the caller's tenant. |
| 409 | `start` greater than `end`. |

### `GET /1/applications/{app_id}/modelPerformance`

**Get per-media predictions from the current best model**

**Auth:** Bearer JWT required

Return the current best model's predictions on the validation (or training) set, paired with the corresponding ground-truth data drawn from the application's subject-media associations. Each item includes the source media, the model prediction(s), and the consensus truth for the given subject, allowing direct inspection of where the model agrees and disagrees with consensus.

Filter by `subject_uid`, `consensus`, and probability range. Sort by raw assertion probability or by per-prediction loss/accuracy. Results are paged via the `cursor` field returned in `paging.next`. If results are not yet computed, the response includes `{"type": "results_pending", "status": ..., "time_to_completion": ..., "description": ...}` and the client should retry after the indicated delay.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Query params:** [ModelPerfRequestV2](#schema-modelperfrequestv2)

**Response:** [ModelPredictionSchema](#schema-modelpredictionschema) — `data` list of per-media prediction objects with `media`, `model_id`, `predictions`, `truth_data`, `app_data_accuracy`, `loss`, and `focus`.

**Errors:**

| Status | Condition |
|---|---|
| 400 | Application has no output subjects. |
| 404 | Application not found in the caller's tenant. |

### `GET /1/applications/{app_id}/performance/newRandom`

**Get performance against a random test sample**

**Auth:** Bearer JWT required

Return performance metrics computed against randomly sampled test data, providing an estimate of model performance against the broader population (as opposed to the curated validation set). Metric format is identical to `releaseValidation`/`currentValidation`. If no random-test runs have completed for this application, the `data` list is empty.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Query params:** [PerformanceSearchSchema](#schema-performancesearchschema)

**Response:** `{"data": [<ApplicationPerformanceSchema>...]}`. See [ApplicationPerformanceSchema](#schema-applicationperformanceschema).

**Errors:**

| Status | Condition |
|---|---|
| 400 | `duration` is non-positive. |
| 404 | Application not found in the caller's tenant. |
| 409 | `start` greater than `end`. |

### `GET /1/applications/{app_id}/feedback`

**Retrieve application feedback (moved)**

**Auth:** Bearer JWT required

This endpoint has moved. Requests are answered with `308 Permanent Redirect` to the v21 feedback endpoint (`/21/applications/{app_id}/feedback`); follow the `Location` header.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

### `POST /1/applications/{app_id}/feedback`

**Submit application feedback (moved)**

**Auth:** Bearer JWT required

This endpoint has moved. Requests are answered with `308 Permanent Redirect` to the v21 feedback endpoint (`/21/applications/{app_id}/feedback`); follow the `Location` header.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

### `POST /1/applications/{app_id}/feedback/purge`

**Purge pending feedback requests**

**Auth:** Bearer JWT required

Discard all pending feedback requests for this application. Use this to clear a backlog of feedback questions that are no longer relevant (for example, after a major application reconfiguration or after a model has been replaced). A feedback-purge event is recorded against the application.

Returns an empty body with status `204` on success.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

### `GET /1/applications/{app_id}/feedback/pending`

**Get pending-feedback count**

**Auth:** Bearer JWT required

Return the number of feedback requests currently awaiting user input for this application.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Response:** `{"pending": <integer>}`.

### `GET /1/applications/{app_id}/replay`

**Get current replay status**

**Auth:** Bearer JWT required

Return whether this application is currently in replay mode and, if so, the subjects being replayed and the replay parameters in use. Replay re-feeds previously processed media back through the application — typically used to re-evaluate historical media against a newer model, or to surface additional candidates for feedback.

When not replaying, the response is `{"replay": false, "replay_subjects": [], "replay_arguments": {}}`. When replaying, `replay_subjects` lists the affected subject UIDs and `replay_arguments` contains the active parameters keyed by subject.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Response:** [ReplaySchema](#schema-replayschema)

**Errors:**

| Status | Condition |
|---|---|
| 400 | An error occurred dispatching the status request. |
| 404 | Application not found in the caller's tenant. |

### `POST /1/applications/{app_id}/replay`

**Start or stop a replay**

**Auth:** Bearer JWT required

Begin replaying media for this application, or stop an in-progress replay. Supply `replay=true` (with at least one of `replay_subjects` or `replay_media`) to start a replay, or `replay=false` to cancel one. Optional filters narrow the media that is replayed: time range, probability range, replay order (`first`, `last`, `random`, `highest_probability`, `lowest_probability`), and a per-subject `limit`.

When replaying subjects that do not belong to the caller's tenant, those subjects must be publicly readable or explicitly shared with the caller's tenant. When replaying a specific media item, the media must belong to the application's tenant.

The response echoes the replay configuration in [ReplaySchema](#schema-replayschema) form, with `replay_arguments` indexed by subject UID.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Request body:** [ReplaySchema](#schema-replayschema)

**Errors:**

| Status | Condition |
|---|---|
| 400 | Neither `replay_subjects` nor `replay_media` supplied; failure dispatching the replay request. |
| 404 | Application not found; supplied `replay_media` not found; caller is not authorized to replay one of the supplied subjects. |

### `GET /1/applications/{app_id}/events`

**List application events**

**Auth:** Bearer JWT required

Return events recorded against this application: model releases, configuration changes, feedback purges, replay activity, and other lifecycle events. Filter by time range and event type. Results are paged via `cursor`.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Query params:** [AppEventSearch](#schema-appeventsearch)

**Response:** `{"data": [<AppEventSchema>...], "paging": {"next": "<url>"}}`. See [AppEventSchema](#schema-appeventschema).

**Errors:**

| Status | Condition |
|---|---|
| 404 | Application not found in the caller's tenant. |

### `GET /1/applications/{app_id}/eventTypes`

**List event types for an application**

**Auth:** Bearer JWT required

Return the list of event types that may be emitted by this application. Use the returned values when filtering `GET /1/applications/{app_id}/events`.

Passing the literal string `all` in place of an `app_id` returns the full set of event types defined across all application types.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier, or the literal `all`. |

**Response:** `{"data": [<string>...]}`.

### `GET /1/applications/{app_id}/consensusHistory`

**Get consensus-count history for the application's output subjects**

**Auth:** Bearer JWT required

Return the historical consensus count for each of the application's output subjects, optionally filtered by user. Results are streamed as a JSON object with a `data` array of timestamped per-subject consensus counts grouped by consensus type. Useful for visualizing how labelled data has accumulated over time.

If no records exist in the requested time window, the most recent record for each subject/consensus-type pair is returned instead. When `start` is omitted, the default window is the year preceding `end` (or the present).

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Query params:** [ConsensusHistorySearch](#schema-consensushistorysearch)

**Response:** streamed JSON `{"data": [<ConsensusHistorySchema>...]}`. See [ConsensusHistorySchema](#schema-consensushistoryschema).

**Errors:**

| Status | Condition |
|---|---|
| 404 | Application not found in the caller's tenant. |

### `POST /1/applications/{app_id}/exportModelToMeraki`

**Export the current model to Meraki**

**Auth:** Bearer JWT required

Export the application's currently released model as a Meraki camera artifact, so it can be deployed to Cisco Meraki MV cameras. The application's `app_type_config.target_execution_hardware` must be `meraki_mv_gen2` or `meraki_mv_gen3`, and the model must use the TFLite backend. The artifact identifier is recorded against the model and is returned in the response.

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | The application identifier. |

**Response:** `{"artifact_id": "<string>", "artifact_name": "<string>"}`.

**Errors:**

| Status | Condition |
|---|---|
| 400 | Application is not targeting Meraki cameras; application has no released model; the model package is not TFLite. |
| 404 | Application not found in the caller's tenant. |
| 412 | Application has no released model. |
| 500 | Failed to read or process the model package; failed to record the exported artifact. |

## Schemas

### `CCPSchema` <a id='schema-ccpschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `application_id` | string | **yes** |  | Identifier of the application this model belongs to. |
| `subject_tag_set` | list[any] | no |  | Legacy alias for `output_subjects`; superseded by `subjects`. |
| `output_subjects` | list[any] | no |  | Output subject UIDs the model emits detections for. |
| `subjects` | list[object] | no |  | Full subject objects corresponding to the application's output subjects. |
| `app_type` | string | no |  | The `application_type` identifier. |
| `release_metrics` | string | no |  | Metric used to select this model release (for example `best_F1`). |
| `num_candidates` | integer | no |  | Total number of candidate models trained for the application. |
| `num_releases` | integer | no |  | Total number of models released for the application. |
| `created_at` | number | no |  | Unix timestamp the application was created. |
| `last_model_update` | number | no |  | Unix timestamp of the most recent model update. |
| `last_candidate_at` | number | no |  | Unix timestamp of the most recent candidate model. |
| `best_model_ccp_url` | string | no |  | Download URL for the released model package. |
| `best_model_ccp_filename` | string | no |  | Filename of the released model package, for use with `GET /1/applications/{app_id}/ccppkg`. |
| `runtime_id` | string | no |  | Runtime identifier associated with the model. |

### `ModelsSchema` <a id='schema-modelsschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `model_id` | string | **yes** |  | Identifier of the released model. |
| `ccp_sha256` | string | **yes** |  | SHA-256 of the model package. |
| `release_time` | number | **yes** |  | Unix timestamp the model was released. |
| `model_image_id` | string | no |  | Identifier of the model's container image. |
| `model_runtime_image` | string | no |  | Model runtime container image reference. |
| `base_runtime_image` | string | no |  | Base runtime container image reference. |

### `ModelsSearch` <a id='schema-modelssearch'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `start` | number \| null | no | default=None | Minimum release timestamp to return. |
| `end` | number \| null | no | default=None | Maximum release timestamp to return. |
| `limit` | integer \| null | no | default=None | Maximum number of results to return. |
| `cursor` | number \| null | no | default=None | Pagination cursor returned by a prior call. |
| `reverse` | boolean \| null | no | default=True | If `true`, sort descending by release time. |

### `PerformanceSearchSchema` <a id='schema-performancesearchschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `start` | number | no | default=None; range(min=0) | Minimum timestamp to return. |
| `end` | number | no | default=None; range(min=0) | Maximum timestamp to return. |
| `duration` | number | no | default=None | Time window (in seconds) ending at the present timestamp, used instead of `start`/`end`. |
| `reverse` | boolean | no | default=False | If `true`, sort descending by time. |
| `limit` | integer \| null | no | range(min=0) | Maximum number of results to return. |

### `ReplaySchema` <a id='schema-replayschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `replay` | boolean | **yes** |  | `true` to start a replay, `false` to stop one. |
| `replay_subjects` | list[string] \| null | no |  | Subject UIDs whose media should be replayed. |
| `replay_media` | string \| null | no |  | Identifier of a specific media item to replay. |
| `foci` | list[any] \| null | no | default=None | Per-media focus regions, when replaying individual media. |
| `validation_only` | boolean | no | default=False | If `true`, restrict the replay to validation-set media. |
| `replay_order` | string \| null | no | default='first'; one of {'first', 'last', 'random', 'highest_probability', 'lowest_probability'} | Order in which to select media to replay. |
| `probability_upper` | number \| null | no | default=1.0; range(min=0, max=1) | Upper bound of subject-media probability to include. |
| `probability_lower` | number \| null | no | default=0.0; range(min=0, max=1) | Lower bound of subject-media probability to include. |
| `time_upper` | number \| null | no | default=None; range(min=0) | Upper bound of subject-media update timestamp to include. |
| `time_lower` | number \| null | no | default=None; range(min=0) | Lower bound of subject-media update timestamp to include. |
| `limit` | number \| null | no | default=1000; range(min=0) | Maximum media items to replay per subject. |
| `force_feedback` | boolean \| null | no | default=False | If `true`, force feedback on all replayed media. |
| `replay_arguments` | any \| null | **yes** |  | Per-subject replay arguments, keyed by subject UID, returned in responses. |
| `replayed` | integer | no |  | Count of media items replayed (returned in responses). |

### `AppEventSchema` <a id='schema-appeventschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `application_id` | string | **yes** |  | Identifier of the application the event was recorded against. |
| `created_at` | number | **yes** |  | Unix timestamp at which the event was recorded. |
| `event_type` | string \| null | no | default=None | Event type (serialized as `type`). |
| `message` | string \| null | no | default=None | Human-readable message describing the event. |
| `event_id` | string \| null | no | default=None | Identifier assigned to this event. |
| `event_data` | string \| null | no | default=None | JSON-encoded structured payload for the event. |

### `AppEventSearch` <a id='schema-appeventsearch'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `start` | number \| null | no | default=None | Minimum event timestamp to return. |
| `end` | number \| null | no | default=None | Maximum event timestamp to return. |
| `limit` | integer \| null | no | default=None | Maximum number of results to return. |
| `cursor` | number \| null | no | default=None | Pagination cursor returned by a prior call. |
| `reverse` | boolean \| null | no | default=False | If `true`, sort descending by time. |
| `event_types` | list[string] | no |  | Restrict results to these event types. |

### `TrainingSummarySchema` <a id='schema-trainingsummaryschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `training_in_progress` | integer | no | default=0 | Number of training runs currently in progress for the application. |

### `CopyApplicationRequestSchema` <a id='schema-copyapplicationrequestschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `source_application_id` | string | no |  | Identifier of the application to copy from. |
| `output_subjects` | list[any] \| null | no | default=None | Output subjects for the new application; if omitted, the source application's output subjects are reused. |
| `app_type_config` | object \| null | no |  | Optional overrides for the new application's type-specific configuration. |

### `DonateApplicationModelRequestSchema` <a id='schema-donateapplicationmodelrequestschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `source_application_id` | string | **yes** |  | Identifier of the application whose released model is being donated. |

### `ApplicationPerformanceSchema` <a id='schema-applicationperformanceschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `app_id` | string | **yes** |  | Identifier of the application. |
| `release_time` | number \| null | no |  | Unix timestamp the model was released. |
| `updated_at` | number \| null | no |  | Unix timestamp at which the metrics were computed. |
| `app_type` | string \| null | no |  | The `application_type` identifier (serialized as `type`). |
| `release_metrics` | string \| null | no |  | Metric used when selecting the model for release. |
| `output_subjects` | list[string] | no |  | Output subjects evaluated. |
| `model_perf` | any | no |  | Overall performance metrics, serialized as `model_performance`. Includes `accuracy`, `F1`, `precision`, `recall`, `TP`, `FP`, `TN`, `FN`. |
| `model_perf_per_subject` | any | no |  | Per-subject performance metrics, serialized as `model_performance_per_subject`, keyed by subject UID with the same metric fields as `model_perf`. |
| `data_count` | integer \| null | no |  | Size of the evaluation dataset. |
| `loss` | number \| null | no | default=None | Model error against the evaluation set. |
| `model_image_id` | string \| null | no |  | Identifier of the model's container image. |
| `model_runtime_image` | string \| null | no |  | Model runtime container image reference. |

### `PredictionSchema` <a id='schema-predictionschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `uncal_prob` | number | **yes** | range(min=0, max=1) | Raw uncalibrated model confidence for this prediction. |

### `ModelPredictionSchema` <a id='schema-modelpredictionschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `assertions` | any | **yes** |  | Raw model assertions for this media (request-side). |
| `ground_truth` | any | **yes** |  | Raw ground-truth payload for this media (request-side). |
| `media_id` | string | **yes** |  | Identifier of the media item. |
| `model_id` | string | **yes** |  | Identifier of the model that produced the predictions. |
| `media` | any | no |  | Media object (full or abridged depending on `abridged_media`). |
| `media_focus_accuracy` | number \| null | no | default=None | Accuracy of the assertion app-data versus the ground truth, serialized as `app_data_accuracy`. |
| `media_focus_loss` | number \| null | no | default=None | Loss of the assertion versus the ground truth, serialized as `loss`. |
| `truth_data` | [SubjectMediaSchema](#schema-subjectmediaschema) | **yes** |  | Ground-truth subject-media items for this media. |
| `predictions` | [PredictionSchema](#schema-predictionschema) | **yes** |  | Model predictions for this media. |
| `focus` | any \| null | no | default=None | Focus region, if any, associated with the prediction. |

### `ModelPerfRequestV2` <a id='schema-modelperfrequestv2'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `subject_uid` | string | **yes** |  | Filter results to the given subject. |
| `consensus` | string | no | default=None | Filter results to the given consensus value (for example `True`, `False`). |
| `abridged_media` | boolean | no | default=False | If `true`, return only `{media_id}` for each media item rather than the full media object. |
| `reverse` | boolean | no | default=False | If `true`, sort descending. |
| `probability_lower` | number | no | default=0.0; range(min=0, max=1) | Lower bound of prediction probability. |
| `probability_upper` | number | no | default=1.0; range(min=0, max=1) | Upper bound of prediction probability. |
| `limit` | integer | no | default=100 | Maximum results per page. |
| `sort` | string | no | default='assertion'; one of {'assertion', 'accuracy', 'loss'} | Sort key for results. |
| `cursor` | string | no | default=None | Pagination cursor returned by a prior call. |
| `set_assignment` | string | no | default='validation'; one of {'training', 'validation'} | Which dataset to draw predictions from. |

### `PredictionSchemaV2` <a id='schema-predictionschemav2'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `uncal_prob` | number | **yes** | range(min=0, max=1) | Raw uncalibrated model confidence for this prediction. |
| `timestamp` | number | **yes** |  | Unix timestamp when the prediction was made (serialized as `created_at`). |

### `ModelPredictionSchemaV2` <a id='schema-modelpredictionschemav2'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `media_id` | string | **yes** |  | Identifier of the media item. |
| `model_id` | string | **yes** |  | Identifier of the model that produced the predictions. |
| `media` | any | no |  | Media object (full or abridged depending on `abridged_media`). |
| `probability` | number \| null | no | default=None | Probability metric for the prediction, serialized as `app_data_accuracy`. |
| `badness` | number \| null | no | default=None | Per-prediction loss/badness score, serialized as `loss`. |
| `truth_data` | [SubjectMediaSchema](#schema-subjectmediaschema) | **yes** |  | Ground-truth subject-media items for this media. |
| `predictions` | [PredictionSchemaV2](#schema-predictionschemav2) | **yes** |  | Model predictions for this media. |
| `focus` | any \| null | no | default=None | Focus region associated with the prediction. |

### `ApplicationQuerySchema` <a id='schema-applicationqueryschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `config_only` | boolean | no | default=False | If `true`, omit model state, training summary, and queued media counts from the response. |

### `ApplicationTypeSchema` <a id='schema-applicationtypeschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `application_type` | string | no | default=None | The application-type identifier. |
| `name` | string | no | default=None | Human-readable name of the application type. |
| `description` | string | no | default=None | Description of the application type. |
| `production` | boolean \| null | no | default=None | `true` for application types that are released for production use. |
| `output_only` | boolean | no | default=False | `true` if the type produces output only (does not consume input subjects). |
| `deprecated` | boolean \| null | no | default=None | `true` if the type is deprecated and should not be used for new applications. |
| `feedback` | boolean | no | default=False | `true` if the type supports user feedback. |
| `default_detection_threshold` | number \| null | no | default=None | Default detection threshold applied to output subjects when an application of this type is created. |
| `custom_fields` | any | no |  | Exposed configuration fields for the type, with type and default/min/max values. |
| `app_manager_dsp_module` | string | no | default=None |  |
| `per_app_dsp` | boolean | no | default=None |  |
| `valid_release_metrics` | list[any] | no |  | Release metrics that may be selected for this application type. |
| `cogniac_model` | boolean | no | default=None | `true` if applications of this type are model-based. |
| `min_output_subjects` | integer | no | default=0; range(min=0) | Minimum number of output subjects required on applications of this type. |
| `max_output_subjects` | integer \| null | no | default=20 | Maximum number of output subjects allowed on applications of this type. |
| `app_data_types` | list[any] \| null | no |  | Supported `app_data_type` values for assertions produced by this type. |
| `video_input` | boolean | no | default=False | `true` if the type accepts video input. |
| `support_detection_threshold` | boolean | no | default=None | `true` if the type honors per-subject detection thresholds. |
| `valid_consensus_types` | list[any] \| null | no |  | Consensus types valid for this application type. |
| `tenant_ids` | list[any] | no |  | Tenants for which this type is available; empty/absent means available to all tenants. |
| `default_release_metrics` | string | no | default=None | The default release metric for applications of this type. |
| `valid_release_metrics` | list[any] \| null | no |  | Release metrics that may be selected for this application type. |
| `input_focus_app_data_types` | list[any] \| null | no |  | `app_data_type` values accepted as input-focus payloads. |
| `execution_targets` | list[string] \| null | no |  | Targets on which the type may execute: `CloudCore`, `EdgeFlow`, `CloudFlow`. |
| `area_focus_pixel_mask_range` | list[any] \| null | no |  | Default range of pixel-mask sizes used for area-focus configuration. |

### `DetectionSchema` <a id='schema-detectionschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `assertion_prefix` | string \| null | no | default=None | Prefix grouping related assertions emitted in the same processing pass. |
| `assertion_id` | string \| null | no | default=None | Identifier of the assertion, serialized as `detection_id`. |
| `user_id` | string \| null | no | default=None | Identifier of the user who supplied the assertion, if any. |
| `model_id` | string \| null | no | default=None | Identifier of the model that produced the assertion, if any. |
| `model_image_id` | string \| null | no | default=None | Identifier of the model's container image, if model-produced. |
| `app_id` | string \| null | no | default=None | Identifier of the application that produced the assertion, if any. |
| `origin` | string \| null | no | default=None; one of {'edgeflow', 'cloudcore'} | Source of the assertion: produced on an EdgeFlow appliance or in CloudCore. |
| `uncal_prob` | number \| null | no | default=None; range(min=0, max=1) | Raw uncalibrated user or model confidence. Absent for subject-capture assertions. |
| `created_at` | number \| null | no | default=None; range(min=0) | Unix timestamp the assertion was created. |
| `prev_prob` | number \| null | no | default=None; range(min=0, max=1) | Subject-media probability before this assertion was applied. |
| `activation` | string \| null | no |  | Activation classification for the assertion. |
| `inference_focus` | any \| null | no |  | Focus region produced by the inference, if any. |

### `AppMediaDetectionSchema` <a id='schema-appmediadetectionschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `detections` | [DetectionSchema](#schema-detectionschema) | **yes** |  | List of detection assertions for this media. |
| `focus` | any \| null | no | default=None | Up-stream focus region carried with the media. |
| `media` | any | no |  | The associated media object. |
| `updated_at` | number | **yes** | range(min=0) | Unix timestamp of media processing, serialized as `timestamp`. |
| `media_list` | any \| null | no | default=None | Related media items, when present. |
| `other_media` | any \| null | no | default=None | Additional media items related to the assertion. |
| `force_feedback` | boolean | no |  | `true` if this media was flagged to force a feedback request. |
| `force_review` | boolean | no |  | `true` if this media was flagged to force review. |

### `SubjectMediaSchema` <a id='schema-subjectmediaschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `subject_uid` | string | **yes** |  | Identifier of the subject. |
| `media_id` | string | no |  | Identifier of the associated media item. |
| `app_data_type` | string \| null | no | default=None | Type of additional app-specific data carried with the association. |
| `app_data` | any \| null | no | default=None | App-specific data payload; structure determined by `app_data_type`. |
| `focus` | any \| null | no | default=None | Focus region associated with the subject-media item. |
| `consensus` | string \| null | no | default=None; one of {'True', 'False', 'Sidelined'} | Consensus value reached for this subject-media association. |
| `result` | string \| null | no | default=None; one of {'True', 'False', 'Sidelined'} | Result value supplied on input (load-only counterpart to `consensus`). |
| `probability` | number | no | range(min=0, max=1) | Probability of the subject-media association. |
| `updated_at` | number | no | range(min=0) | Unix timestamp of the last update, serialized as `update_timestamp`. |

### `ConsensusHistorySchema` <a id='schema-consensushistoryschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `timestamp` | number | **yes** |  | Unix timestamp of the record, rounded to the nearest minute. |
| `count` | integer | **yes** |  | Number of subject-media items at consensus at the given timestamp. |

### `ConsensusHistorySearch` <a id='schema-consensushistorysearch'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `user_id` | string | no | default=None | If supplied, restrict the history to consensus contributed by this user. |
| `start` | number | no | default=None | Minimum timestamp to return. Defaults to one year before `end`. |
| `end` | number | no | default=None | Maximum timestamp to return. Defaults to the present. |
| `limit` | integer | no | default=None | Maximum number of records to return. |
| `reverse` | boolean | no | default=False | If `true`, sort descending by time. |
