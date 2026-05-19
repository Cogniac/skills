# feedback-service-api

Manage the human-in-the-loop feedback queue for a Cogniac application. Operators schedule media items (optionally narrowed to a region of interest) for review, reviewers pull pending work, and reviewers submit labeling decisions that are aggregated into consensus training data for the application's output subjects.

A typical workflow:

1. An operator (or upstream service) calls `POST /21/applications/{app_id}/feedbackRequests` to enqueue a media item for review. The response carries a `feedback_request_id`.
2. Reviewers assigned to the application call `GET /21/applications/{app_id}/feedbackRequests/pending` to fetch outstanding work, or `GET /21/applications/{app_id}/feedbackRequests/count` to see how much is queued.
3. Each reviewer submits their decision with `POST /21/applications/{app_id}/feedback`, referencing the `feedback_request_id`. A reviewer may later revise their answer with `PUT /21/applications/{app_id}/feedback`, supplying the `feedback_id` returned in the original response.
4. Once the configured minimum number of responses (`total_response_count_min`) has been received, the feedback request is considered satisfied and is retired from the queue.

Reviewers must be assigned to the target application as `annotator` or `expert_annotator` (see the `reviewers` field on the application object). Feedback requests scheduled with a specific `roles` list are only visible to reviewers with a matching role; requests scheduled with `["anyone"]` are visible to all eligible users in the tenant.

All endpoints below are served under the `/21` API version prefix.

## Endpoints

### `GET /21/feedback/version`

Return the service's running API version and build identifier. Intended for health-check and version-pinning use.

**Auth:** no auth required

### `POST /21/applications/{app_id}/feedbackRequests`

Schedule a feedback request for a media item (and optional focus region) on the given application. The response contains the generated `feedback_request_id`, which callers reference when retrieving or submitting feedback for this request.

If a feedback request already exists for the same `(media_id, focus)` pair on the application and still needs reviewer input, the existing request is re-surfaced rather than duplicated. If an existing request has already been satisfied and does not need further input, the service responds with `409 Conflict`.

`total_response_count_min` must be an odd integer so that tie-breaking is well-defined when reviewers disagree. Set `per_reviewer_response_count_max` to `1` for the common case where each reviewer should answer at most once.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | Identifier of the application the feedback request targets. |

**Request body:** [ScheduleFeedbackRequestsSchema](#schema-schedulefeedbackrequestsschema)

**Responses:**

| Status | Description |
|---|---|
| 201 | Feedback request scheduled; body is the stored request (`ScheduleFeedbackRequestsSchema`). |
| 409 | A satisfied feedback request already exists for the same media and focus on this application. |

### `DELETE /21/applications/{app_id}/feedbackRequests`

Mark all feedback requests for the application for removal. After this call, currently scheduled feedback requests for `app_id` will no longer be returned to reviewers and will be pruned in the background.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | Identifier of the application whose feedback queue should be cleared. |

**Responses:**

| Status | Description |
|---|---|
| 204 | Purge has been scheduled. |

### `GET /21/applications/{app_id}/feedbackRequests/pending`

Return the feedback requests on `app_id` that are available to the calling user for review.

A feedback request is returned if both of the following hold:

- The caller's tenant role satisfies the request's `roles` constraint. A request scheduled with `["anyone"]` is available to all eligible users; a request scheduled with one of the annotator roles (e.g., `annotator`, `expert_annotator`) is only returned to users holding that role on the tenant.
- The request has not yet received `total_response_count_min` responses, and the caller has not already submitted `per_reviewer_response_count_max` responses to it.

Each returned item includes the media descriptor and the focus region (if any) so that the reviewer client can render the item without an additional lookup.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | Identifier of the application. |

**Query params:**

| Name | Type | Description |
|---|---|---|
| `limit` | integer | Maximum number of pending feedback requests to return. |

**Responses:**

| Status | Description |
|---|---|
| 200 | `{ "data": [ FeedbackRequestSchema, ... ] }` — see [FeedbackRequestSchema](#schema-feedbackrequestschema). |

### `GET /21/applications/{app_id}/feedbackRequests/count`

Return the number of feedback requests on `app_id` currently available to the calling user (subject to the same eligibility rules as the `pending` endpoint).

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | Identifier of the application. |

**Query params:**

| Name | Type | Description |
|---|---|---|
| `limit` | integer | Upper bound on the count returned. |

**Responses:**

| Status | Description |
|---|---|
| 200 | `{ "count": <integer> }` |

### `GET /21/applications/{app_id}/feedback`

Retrieve a single feedback response that the calling user previously submitted against a specific feedback request. Both `feedback_request_id` and `feedback_id` are required query parameters.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | Identifier of the application. |

**Query params:** [FeedbackQuerySchema](#schema-feedbackqueryschema)

**Responses:**

| Status | Description |
|---|---|
| 200 | The stored feedback response (`FeedbackResponseSchema`). |
| 404 | The feedback request or the user's feedback within it was not found. |

### `POST /21/applications/{app_id}/feedback`

Submit a reviewer's feedback response. The request body must reference the feedback request via `feedback_request_id`; `media_id` and `focus` are resolved from that request and need not be repeated. The response includes a `feedback_id` that the caller can use later to fetch or update this specific submission.

When the request scheduling required a particular reviewer role, the caller must hold that role on the tenant; otherwise the call returns `404`.

`feedback_id` must not be set on a `POST`; use `PUT` to revise an existing submission.

Each entry in the `subjects` array carries the reviewer's verdict for one of the application's output subjects via the `result` field (`"True"`, `"False"`, or `"Sidelined"`). When `result` is `"Sidelined"`, all of the application's output subjects must be present in `subjects` and all must be set to `"Sidelined"`.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | Identifier of the application. |

**Request body:** [FeedbackResponseSchema](#schema-feedbackresponseschema)

**Responses:**

| Status | Description |
|---|---|
| 200 | Feedback accepted; body is the stored feedback response, including `feedback_id`. |
| 400 | Body validation failed, or `feedback_id` was supplied. |
| 404 | The referenced feedback request does not exist, or the caller is not assigned a reviewer role required by the request. |

### `PUT /21/applications/{app_id}/feedback`

Revise a feedback response that the caller previously submitted for a feedback request. Both `feedback_request_id` and `feedback_id` are required.

A `PUT` records a new assertion against the feedback request rather than replacing prior assertions in place; the `feedback_id` is the handle clients use to associate a revision with the user's previous submission.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | Identifier of the application. |

**Request body:** [FeedbackResponseSchema](#schema-feedbackresponseschema)

**Responses:**

| Status | Description |
|---|---|
| 200 | Update accepted; body is the stored feedback response. |
| 400 | Missing `feedback_request_id` or `feedback_id`. |
| 404 | The referenced feedback request does not exist, or the caller is not assigned a reviewer role required by the request. |

## Schemas

### `ScheduleFeedbackRequestsSchema` <a id='schema-schedulefeedbackrequestsschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `feedback_request_id` | string | no |  | Server-assigned identifier of the resulting feedback request (read-only). |
| `app_id` | string | no |  | Application the feedback request belongs to. |
| `media_id` | string | **yes** |  | Media item the reviewer is being asked about. |
| `focus` | [FocusSchema](#schema-focusschema) \| null | no |  | Region within the media for which feedback is being requested. |
| `roles` | list[string] | no | length(min=1) | Reviewer roles eligible to respond. Use `["anyone"]` to admit all eligible tenant users. |
| `per_reviewer_response_count_max` | integer | **yes** | default=1 | Maximum number of responses a single reviewer may submit for this request. |
| `total_response_count_min` | integer | no | default=1 | Minimum number of total responses required before the request is considered complete. |
| `total_feedback_count` | integer | no | default=0 | Number of responses received so far (read-only). |
| `subjects` | list[[ScheduleFeedbackRequestAssertionSchema](#schema-schedulefeedbackrequestassertionschema)] \| null | no | default=None | Preliminary subject-media assertions to seed the request with. |
| `created_at` | number | no | range(min=0) | Creation timestamp (Unix epoch seconds; read-only). |
| `modified_at` | number | no | range(min=0) | Last-modified timestamp (Unix epoch seconds; read-only). |

### `ScheduleFeedbackRequestAssertionSchema` <a id='schema-schedulefeedbackrequestassertionschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `subject_uid` | string | no | default=None | Subject this assertion is about. |
| `media_id` | string | **yes** |  | Media item the assertion applies to. |
| `focus` | any \| null | no | default=None | Region within the media the assertion applies to. |
| `probability` | number | no | default=None; range(min=0, max=1) | Model probability for the assertion, if any. |
| `app_data_type` | string \| null | no | default=None | Application-type-specific payload kind for `app_data`. |
| `app_data` | any \| null | no | default=None | Application-type-specific assertion payload (e.g., bounding-box coordinates). |
| `consensus` | string \| null | no | default=None; one of {'True', 'False', 'Sidelined'} | Pre-existing consensus value to seed the request with. |
| `feedback_metrics` | list[any] \| null | no |  | Per-assertion metrics. |
| `contra_model` | boolean | no | default=None | Whether this assertion contradicts the model's prediction. |

### `FocusSchema` <a id='schema-focusschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `box` | [BoxFocusSchema](#schema-boxfocusschema) | **yes** |  | Bounding box of the focus region. |
| `area_mask_png` | string | no | length(min=92) | Base64-encoded PNG mask describing the focus area. |
| `area_mask_media_id` | string | no |  | Identifier of a media item holding the focus-area mask. |
| `pixel_mask_scale` | integer | no | default=8; one of {1, 2, 4, 8, 16, 32} | Downscale factor applied to the pixel mask. |
| `area_mask_rle` | [RLESchema](#schema-rleschema) | no |  | Run-length-encoded focus-area mask. |

### `BoxFocusSchema` <a id='schema-boxfocusschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `x0` | integer | **yes** | range(min=0) | Left coordinate of the box, in pixels. |
| `x1` | integer | **yes** | range(min=0) | Right coordinate of the box, in pixels. |
| `y0` | integer | **yes** | range(min=0) | Top coordinate of the box, in pixels. |
| `y1` | integer | **yes** | range(min=0) | Bottom coordinate of the box, in pixels. |

### `RLESchema` <a id='schema-rleschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `size` | list[integer] | **yes** | length(equal=2) | Mask dimensions as `[height, width]` in pixels. |
| `counts` | string | **yes** | length(min=1) | COCO-style run-length-encoded mask payload. |
| `box` | [boxSchema](#schema-boxschema) | no |  | Optional bounding box around the mask. |

### `boxSchema` <a id='schema-boxschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `x0` | integer | **yes** | range(min=0) | Left coordinate of the box, in pixels. |
| `x1` | integer | **yes** | range(min=0) | Right coordinate of the box, in pixels. |
| `y0` | integer | **yes** | range(min=0) | Top coordinate of the box, in pixels. |
| `y1` | integer | **yes** | range(min=0) | Bottom coordinate of the box, in pixels. |

### `FeedbackRequestSchema` <a id='schema-feedbackrequestschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `feedback_request_id` | string | no | default=None | Identifier of the feedback request. |
| `app_id` | string | no |  | Application the request belongs to. |
| `media_id` | string | **yes** |  | Media item to be reviewed. |
| `media` | any | no |  | Media descriptor needed to render the item in a reviewer client. |
| `other_media` | any \| null | no |  | Auxiliary media (e.g., reference frames) associated with the request. |
| `media_list` | any \| null | no |  | Additional media items associated with the request. |
| `subjects` | list[[FeedbackRequestAssertionSchema](#schema-feedbackrequestassertionschema)] \| null | no | default=None | Pre-existing subject-media assertions associated with the request. |
| `reason` | string \| null | no | default=None | Optional reason the request was scheduled. |
| `focus` | any \| null | no | default=None | Region within the media for which feedback is being requested. |

### `FeedbackRequestAssertionSchema` <a id='schema-feedbackrequestassertionschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `subject_uid` | string | no | default=None | Subject this assertion is about. |
| `media_id` | string | **yes** |  | Media item the assertion applies to. |
| `focus` | any \| null | no | default=None | Region within the media the assertion applies to. |
| `probability` | number | no | default=None; range(min=0, max=1) | Model probability for the assertion, if any. |
| `app_data_type` | string \| null | no | default=None | Application-type-specific payload kind for `app_data`. |
| `app_data` | any \| null | no | default=None | Application-type-specific assertion payload. |

### `FeedbackQuerySchema` <a id='schema-feedbackqueryschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `feedback_request_id` | string \| null | **yes** |  | Identifier of the feedback request whose responses are being queried. |
| `feedback_id` | string \| null | **yes** |  | Identifier of a specific feedback response. |

### `FeedbackResponseSchema` <a id='schema-feedbackresponseschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `app_id` | string | no |  | Application the response is associated with (read-only). |
| `tenant_id` | string | no |  | Tenant the response is associated with (read-only). |
| `user_id` | string | no |  | Reviewer who submitted the response (read-only). |
| `media_id` | string \| null | no |  | Media item the response covers. |
| `focus` | any \| null | no |  | Region within the media the response covers. |
| `feedback_request_id` | string \| null | no |  | Feedback request this response is for. |
| `feedback_id` | string \| null | no |  | Identifier of this response; supply on `PUT` to revise a previously submitted response. |
| `decision_time` | number \| null | no | default=None | Time at which the reviewer made the decision (Unix epoch seconds). |
| `subjects` | list[[FeedbackResponseAssertionSchema](#schema-feedbackresponseassertionschema)] \| null | **yes** |  | Subject-media assertions making up the reviewer's verdict. Each element corresponds to one of the application's output subjects; for application types like `box_detection` the per-subject `app_data` carries the geometric detail. The list length depends on the application type and the `result` values used. |
| `client_data` | [ClientDataSchema](#schema-clientdataschema) \| null | no | default=None | Reviewer-client context (software version, device, interface). |

### `FeedbackResponseAssertionSchema` <a id='schema-feedbackresponseassertionschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `subject_uid` | string | **yes** |  | Output subject this assertion is about. |
| `media_id` | string | no |  | Media item the assertion applies to. |
| `app_data_type` | string \| null | no | default=None | Application-type-specific payload kind for `app_data`. |
| `app_data` | any \| null | no | default=None | Application-type-specific assertion payload (e.g., bounding-box coordinates for `box_detection`). |
| `focus` | any \| null | no | default=None | Region within the media the assertion applies to. |
| `result` | string \| null | no | default=None; one of {'True', 'False', 'Sidelined'} | Reviewer's verdict for this subject on this media item. |
| `uncal_prob` | number | no | range(min=0, max=1) | Uncalibrated probability associated with the assertion, if any. |

### `ClientDataSchema` <a id='schema-clientdataschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `sw_version` | string | no |  | Reviewer-client software version. |
| `device` | string | no |  | Device the reviewer-client is running on. |
| `interface` | string | no |  | Reviewer-client interface identifier. |
| `interface_version` | string | no | default='v1' | Reviewer-client interface version. |
