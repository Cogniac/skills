# evaluation-metrics-api

Manage the per-application evaluation metrics that Cogniac CloudCore uses to score model performance. An evaluation metric pairs a metric family (for example F1, ROC, IoU, Dice score, or count-based variants) with the parameters that control how detections are matched against ground truth (detection thresholds, IoU thresholds, pixel-distance tolerances, averaging method, and per-output-subject weights). Each application may have multiple registered metrics; exactly one of the active metrics is designated as the application's **primary** metric, which is the one used to rank candidate models during training and to drive release decisions.

Customers interact with this service in two ways. App managers (tenant administrators who are listed on the application's `app_managers`) use `POST /22/applications/{application_id}/evaluation_metrics` to register additional metrics, swap which metric is primary, or soft-delete a metric. Callers fetch the current set of metrics with `GET /22/applications/{application_id}/evaluation_metrics`. A separate schemas endpoint (`GET /22/schemas/evaluation_metrics`) returns the JSON Schema for every supported metric type so clients can build forms or validate requests offline.

A few invariants are worth knowing before integrating. An application can have at most **five** active evaluation metrics. The primary metric cannot be deleted directly — set a different metric as primary first and then delete the old one. "Deletion" is a soft delete (`active=0`); the record remains and can be re-activated by re-registering the same metric parameters. All endpoints are served under the `/22/` API version prefix.

## Endpoints

### `EvaluationMetrics`

#### `GET /22/applications/{application_id}/evaluation_metrics` <a id='op-get-22-applications--application-id--evaluation-metrics-get'></a>

**List evaluation metrics for an application.**

Returns every registered evaluation metric for the application, ordered so that the primary metric is first, followed by the remaining active metrics (sorted by `active_timestamp`), and then inactive metrics if `show_inactive=true` is supplied. The caller's tenant must own the application.

By default, `detection_thresholds` are returned in their fully expanded, per-output-subject form. Pass `abridged=true` to receive the compact representation in which the most common threshold value is collapsed into a single `default` key.

**Auth:** Bearer JWT; required roles: `{tenant_admin, tenant_user, tenant_viewer}`

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `application_id` | path | string | **yes** | Identifier of the application to read metrics for. |
| `show_inactive` | query | boolean \| null | no | When `true`, include soft-deleted (inactive) metrics in the response. Defaults to `false`. |
| `sort_by_active_timestamp_desc` | query | boolean \| null | no | When `true` (default), active metrics are returned newest-first by `active_timestamp`. Set `false` to reverse the order. |
| `abridged` | query | boolean \| null | no | When `true`, return `detection_thresholds` in the compact `{"default": value}` form rather than expanded per output subject. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | List of all the evaluation metrics | `application/json` → list[[GetApplicationEvaluationMetricResponse](#schema-getapplicationevaluationmetricresponse)] |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 403 | The application is not owned by the caller's tenant. |

#### `POST /22/applications/{application_id}/evaluation_metrics` <a id='op-post-22-applications--application-id--evaluation-metrics-post'></a>

**Register, set primary, or delete an evaluation metric.**

Single mutating entry point for an application's evaluation metric set. The combination of `active` and `primary` in the request body selects the operation:

- `active=1, primary=0` — register a new (non-primary) metric, or re-activate a previously deleted one with the same parameters.
- `active=1, primary=1` — register the metric if needed and promote it to be the application's primary metric, demoting the previous primary.
- `active=0, primary=0` — soft-delete the metric (sets `active=0`). The metric record is retained and can be re-activated by re-registering with the same parameters.
- `active=0, primary=1` — rejected; the primary metric cannot be deleted.

The metric `name` is validated against the application's `type` (different app types support different metric families). Backward-compatible metric aliases are accepted and normalized. The caller's tenant must own the application, and the caller must either hold the `cogniac_admin` role or be listed in the application's `app_managers`.

**Auth:** Bearer JWT; required roles: `{cogniac_admin, tenant_admin}` (caller must also be listed as an app manager on the application unless the caller has `cogniac_admin`)

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `application_id` | path | string | **yes** | Identifier of the application whose metrics are being modified. |

**Request body** (`application/json`, required: **yes**): [PostEvaluationMetricRequest](#schema-postevaluationmetricrequest)

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | evaluation_metric response | `application/json` → [GetApplicationEvaluationMetricResponse](#schema-getapplicationevaluationmetricresponse) |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 400 | The application's type is not supported, the supplied metric `name` is not valid for the application type, or a write was attempted against an existing primary metric. |
| 403 | The application is not owned by the caller's tenant; the caller is not listed in `app_managers` (and is not `cogniac_admin`); or the limit of five active evaluation metrics has been reached. |
| 404 | A delete or re-activate was requested but no evaluation metric exists for the supplied parameters. |
| 409 | `active=0` and `primary=1` were supplied together (primary metric cannot be deleted). |

### `EvaluationMetricsSchemas`

#### `GET /22/schemas/evaluation_metrics` <a id='op-get-22-schemas-evaluation-metrics-get'></a>

**Return the JSON Schema for evaluation metrics.**

Returns the JSON Schema describing the request shape for a single evaluation metric. With no query parameter, returns a map of metric name to schema for every supported metric. Pass `name` to fetch the schema for a single metric (for example `box_F1` or `segmentation_IoU`). Useful for clients that want to render dynamic forms or validate metric configurations client-side.

**Auth:** Bearer JWT required

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `name` | query | string | no | Optional metric name. When supplied, the response contains only that metric's schema; otherwise, schemas for all supported metrics are returned. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Evaluation metric schema | `application/json` → any |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 400 | The supplied `name` is not a supported evaluation metric. |

### `default`

#### `HEAD /` <a id='op-get-api-version--head'></a>

**Service health check.**

Lightweight reachability probe. Returns the service's API version.

**Auth:** no auth required

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | `application/json` → any |

#### `GET /22/evaluation_metrics/version` <a id='op-get-api-version-22-evaluation-metrics-version-get'></a>

**Return the service API version.**

Returns the integer API version implemented by this service. Use to verify the deployed build before issuing version-sensitive calls.

**Auth:** no auth required

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | `application/json` → any |

---

## Schema Components

All Pydantic-derived schemas referenced above. Constraints (enum, range, length, pattern, default) are inline so an API consumer can write a correct client without reading Pydantic source.

### `AreaDetectionFPR` <a id='schema-areadetectionfpr'></a>

Area-based detection metric scored at a fixed detection threshold (F1 / precision / recall variants).

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `detection_thresholds` | dict[str, string] \| list[dict[str, string]] \| null | no | default={'default': '0.5'} | Per-output-subject detection thresholds. Accepts the compact `{"default": value}` form or the expanded per-subject form. |
| `max_is_better` | boolean | no | default=True | Indicates that larger metric values are better (used by the training pipeline to pick the best model). |
| `name` | Literal['area_F1', 'area_any_F1', 'area_precision', 'area_any_precision', 'area_recall', 'area_any_recall'] | **yes** | | Specific area-detection metric variant. |

### `AreaDetectionROC` <a id='schema-areadetectionroc'></a>

Area-based detection metric scored as an area under a curve (ROC or precision-recall) across thresholds.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `max_is_better` | boolean | no | default=True | Larger metric values are better. |
| `name` | Literal['area_ROC', 'area_precision_recall'] | **yes** | | Specific area-detection curve metric. |

### `BoxDetectionFPR` <a id='schema-boxdetectionfpr'></a>

Bounding-box detection metric scored at a fixed detection threshold. A predicted box is considered a match to a ground-truth box when their IoU exceeds `iou_threshold`.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `detection_thresholds` | dict[str, string] \| list[dict[str, string]] \| null | no | default={'default': '0.5'} | Per-output-subject detection thresholds (compact or expanded form). |
| `iou_threshold` | string \| null | no | default='0.25' | Minimum IoU between predicted and ground-truth boxes for a positive match. |
| `max_is_better` | boolean | no | default=True | Larger metric values are better. |
| `name` | Literal['box_F1', 'box_any_F1', 'box_precision', 'box_any_precision', 'box_recall', 'box_any_recall'] | **yes** | | Specific box-detection metric variant. |

### `BoxDetectionROC` <a id='schema-boxdetectionroc'></a>

Bounding-box detection metric scored as an area under a curve.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `iou_threshold` | string \| null | no | default='0.25' | Minimum IoU between predicted and ground-truth boxes for a positive match. |
| `max_is_better` | boolean | no | default=True | Larger metric values are better. |
| `name` | Literal['box_ROC', 'box_precision_recall'] | **yes** | | Specific box-detection curve metric. |

### `BoxProbabilityDistance` <a id='schema-boxprobabilitydistance'></a>

Bounding-box metric that scores the distance between predicted and ground-truth probability distributions; lower is better.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `detection_thresholds` | dict[str, string] \| list[dict[str, string]] \| null | no | default={'default': '0.5'} | Per-output-subject detection thresholds. |
| `iou_threshold` | string \| null | no | default='0.25' | Minimum IoU between predicted and ground-truth boxes for matching. |
| `max_is_better` | boolean | no | default=False | Smaller metric values are better. |
| `name` | Literal['box_probability_distance'] | **yes** | | |

### `CountEuclidean` <a id='schema-counteuclidean'></a>

Count-based metric measuring Euclidean (or normalized Euclidean) distance between predicted and ground-truth subject counts.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `detection_thresholds` | dict[str, string] \| list[dict[str, string]] \| null | no | default={'default': '0.5'} | Per-output-subject detection thresholds. |
| `max_is_better` | boolean | no | default=False | Smaller distances are better. |
| `name` | Literal['count_euclidean', 'count_normalized_euclidean'] | **yes** | | |

### `FullframeFPR` <a id='schema-fullframefpr'></a>

Full-frame classification metric scored at a fixed detection threshold.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `detection_thresholds` | dict[str, string] \| list[dict[str, string]] \| null | no | default={'default': '0.5'} | Per-output-subject detection thresholds. |
| `max_is_better` | boolean | no | default=True | Larger metric values are better. |
| `name` | Literal['F1', 'precision', 'recall'] | **yes** | | Specific full-frame metric variant. |

### `FullframeROC` <a id='schema-fullframeroc'></a>

Full-frame classification metric scored as an area under a curve.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `max_is_better` | boolean | no | default=True | Larger metric values are better. |
| `name` | Literal['ROC', 'precision_recall'] | **yes** | | Specific full-frame curve metric. |

### `GetApplicationEvaluationMetricResponse` <a id='schema-getapplicationevaluationmetricresponse'></a>

Stored representation of a registered evaluation metric.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `active` | integer | **yes** | | `1` if the metric is currently active, `0` if it has been soft-deleted. |
| `active_timestamp` | string | **yes** | pattern='^(?!^[-+.]*$)[+-]?0*\\d*\\.?\\d*$' | Unix timestamp (as a decimal string) of the metric's most recent activation. |
| `evaluation_metric` | [FullframeFPR](#schema-fullframefpr) \| [FullframeROC](#schema-fullframeroc) \| [BoxDetectionFPR](#schema-boxdetectionfpr) \| [BoxDetectionROC](#schema-boxdetectionroc) \| [BoxProbabilityDistance](#schema-boxprobabilitydistance) \| [PointDetectionFPR](#schema-pointdetectionfpr) \| [PointDetectionROC](#schema-pointdetectionroc) \| [AreaDetectionFPR](#schema-areadetectionfpr) \| [AreaDetectionROC](#schema-areadetectionroc) \| [PointCountFPR](#schema-pointcountfpr) \| [PointCountROC](#schema-pointcountroc) \| [CountEuclidean](#schema-counteuclidean) \| [OcrFPR](#schema-ocrfpr) \| [OcrROC](#schema-ocrroc) \| [SegmentationIoU](#schema-segmentationiou) \| [SegmentationDiceScore](#schema-segmentationdicescore) | **yes** | | The metric's name and parameters, typed by metric family. |
| `evaluation_metric_hash` | string | **yes** | | Deterministic hash of the metric parameters; used as a stable identifier in subsequent requests. |
| `primary` | integer | **yes** | | `1` if this is the application's primary metric, otherwise `0`. |
| `user_tag` | string \| null | no | | Optional user-supplied tag carried alongside the metric for tracking purposes. |

### `HTTPValidationError` <a id='schema-httpvalidationerror'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `detail` | list[[ValidationError](#schema-validationerror)] | no | | One entry per validation failure. |

### `OcrFPR` <a id='schema-ocrfpr'></a>

OCR (text-recognition) metric scored at a fixed detection threshold.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `detection_thresholds` | dict[str, string] \| list[dict[str, string]] \| null | no | default={'default': '0.5'} | Per-output-subject detection thresholds. |
| `max_is_better` | boolean | no | default=True | Larger metric values are better. |
| `name` | Literal['ocr_F1', 'ocr_precision', 'ocr_recall'] | **yes** | | Specific OCR metric variant. |

### `OcrROC` <a id='schema-ocrroc'></a>

OCR metric scored as an area under a curve.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `max_is_better` | boolean | no | default=True | Larger metric values are better. |
| `name` | Literal['ocr_ROC', 'ocr_precision_recall'] | **yes** | | Specific OCR curve metric. |

### `PointCountFPR` <a id='schema-pointcountfpr'></a>

Point-counting metric scored at a fixed detection threshold. A predicted point matches ground truth when it lies within `pixel_distance_tolerance` pixels.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `count_tolerance` | integer \| null | no | default=0 | Allowed absolute difference between predicted and ground-truth counts before the prediction is marked incorrect. |
| `detection_thresholds` | dict[str, string] \| list[dict[str, string]] \| null | no | default={'default': '0.5'} | Per-output-subject detection thresholds. |
| `max_is_better` | boolean | no | default=True | Larger metric values are better. |
| `name` | Literal['point_count_F1', 'point_count_precision', 'point_count_recall'] | **yes** | | Specific point-count metric variant. |
| `pixel_distance_tolerance` | string \| null | no | default='16' | Maximum pixel distance between a predicted point and a ground-truth point for a positive match. |
| `subject_weights` | dict[str, number] \| null | no | | Optional per-output-subject weights used when aggregating the metric across subjects. |

### `PointCountROC` <a id='schema-pointcountroc'></a>

Point-counting metric scored as an area under a curve.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `count_tolerance` | integer \| null | no | default=0 | Allowed absolute count difference before the prediction is marked incorrect. |
| `max_is_better` | boolean | no | default=True | Larger metric values are better. |
| `name` | Literal['point_count_ROC', 'point_count_precision_recall'] | **yes** | | Specific point-count curve metric. |
| `pixel_distance_tolerance` | string \| null | no | default='16' | Maximum pixel distance between predicted and ground-truth points for a positive match. |

### `PointDetectionFPR` <a id='schema-pointdetectionfpr'></a>

Point-detection metric scored at a fixed detection threshold.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `detection_thresholds` | dict[str, string] \| list[dict[str, string]] \| null | no | default={'default': '0.5'} | Per-output-subject detection thresholds. |
| `max_is_better` | boolean | no | default=True | Larger metric values are better. |
| `name` | Literal['point_F1', 'point_any_F1', 'point_precision', 'point_any_precision', 'point_recall', 'point_any_recall'] | **yes** | | Specific point-detection metric variant. |
| `pixel_distance_tolerance` | string \| null | no | default='4' | Maximum pixel distance between predicted and ground-truth points for a positive match. |

### `PointDetectionROC` <a id='schema-pointdetectionroc'></a>

Point-detection metric scored as an area under a curve.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `max_is_better` | boolean | no | default=True | Larger metric values are better. |
| `name` | Literal['point_ROC', 'point_precision_recall'] | **yes** | | Specific point-detection curve metric. |
| `pixel_distance_tolerance` | string \| null | no | default='4' | Maximum pixel distance between predicted and ground-truth points for a positive match. |

### `PostEvaluationMetricRequest` <a id='schema-postevaluationmetricrequest'></a>

Body for register / set-primary / delete operations. The combination of `active` and `primary` selects the operation (see the endpoint description for `POST /22/applications/{application_id}/evaluation_metrics`).

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `active` | integer | **yes** | | `1` to register or re-activate; `0` to soft-delete. |
| `averaging_method` | string \| null | no | | For segmentation metrics, how to aggregate across subjects (`aggregated` or `mean_over_subjects`). |
| `candidates` | list[string] | no | default=['name', 'detection_thresholds', 'iou_threshold', 'dice_score_threshold', 'pixel_distance_tolerance', 'count_tolerance', 'level', 'averaging_method', 'subject_weights', 'user_tag'] | Names of fields from this request that should be carried into the constructed evaluation metric when non-null. Override only if you need to suppress a field. |
| `count_tolerance` | integer \| null | no | | See the per-metric schema for semantics. |
| `detection_thresholds` | list[dict[str, number \| string]] \| null | no | | Per-output-subject detection thresholds, supplied as a list of single-entry dicts. |
| `dice_score_threshold` | number \| string \| null | no | | Threshold used by Dice-score segmentation metrics. |
| `iou_threshold` | number \| string \| null | no | | Threshold used by IoU-based metrics. |
| `level` | string \| null | no | | For segmentation metrics, the scoring level (`pixel`, `instance`, or `image`). |
| `name` | string \| null | no | | Metric name (for example `box_F1`, `segmentation_IoU`). Backward-compatible aliases are accepted and normalized. |
| `pixel_distance_tolerance` | number \| string \| null | no | | Pixel-distance tolerance for point-based metrics. |
| `primary` | integer \| null | no | | `1` to make this the application's primary metric. Mutually exclusive with `active=0`. |
| `subject_weights` | dict[str, number] \| null | no | | Optional per-output-subject weights for metric aggregation. |
| `user_tag` | string \| null | no | | Free-form caller-supplied label stored with the metric. |

### `SegmentationDiceScore` <a id='schema-segmentationdicescore'></a>

Segmentation metric scored by Dice coefficient.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `averaging_method` | Literal['aggregated', 'mean_over_subjects'] \| null | no | default='mean_over_subjects' | How the score is aggregated across output subjects. |
| `detection_thresholds` | dict[str, string] \| list[dict[str, string]] \| null | no | default={'default': '0.5'} | Per-output-subject detection thresholds. |
| `dice_score_threshold` | number \| null | no | default='0.25' | Minimum Dice score for a predicted mask to count as a match. |
| `level` | Literal['pixel', 'instance', 'image'] \| null | no | default='instance' | Granularity at which the score is computed. |
| `max_is_better` | boolean | no | default=True | Larger metric values are better. |
| `name` | Literal['segmentation_DiceScore'] | **yes** | | |

### `SegmentationIoU` <a id='schema-segmentationiou'></a>

Segmentation metric scored by intersection-over-union.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `averaging_method` | Literal['aggregated', 'mean_over_subjects'] \| null | no | default='mean_over_subjects' | How the score is aggregated across output subjects. |
| `detection_thresholds` | dict[str, string] \| list[dict[str, string]] \| null | no | default={'default': '0.5'} | Per-output-subject detection thresholds. |
| `iou_threshold` | number \| null | no | default='0.25' | Minimum IoU between predicted and ground-truth masks for a positive match. |
| `level` | Literal['pixel', 'instance', 'image'] \| null | no | default='instance' | Granularity at which the score is computed. |
| `max_is_better` | boolean | no | default=True | Larger metric values are better. |
| `name` | Literal['segmentation_IoU'] | **yes** | | |

### `ValidationError` <a id='schema-validationerror'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `ctx` | object | no | | Additional context for the validation error. |
| `input` | any | no | | The offending input value. |
| `loc` | list[string \| integer] | **yes** | | JSON-pointer-style location of the field that failed validation. |
| `msg` | string | **yes** | | Human-readable description of the error. |
| `type` | string | **yes** | | Machine-readable validation-error type identifier. |
