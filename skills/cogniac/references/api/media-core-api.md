# media-core-api

The Media Core API handles ingestion, retrieval, and lifecycle management of media (images and video) used as inputs to Cogniac applications. Customer workflows typically push media in via `POST /1/media` (images) or the resumable video flow, query media by content hash / external identifier, and then retrieve the resulting application detections and subject associations.

All endpoints require a Bearer JWT in the `Authorization` header and operate within the caller's tenant. Media uploaded under one tenant is not visible to other tenants.

## Endpoints

### `POST /1/media`

**Upload new image data**

Upload a new image into the caller's tenant. The image becomes available to applications via subject associations and is referenced in subsequent requests by the returned `media_id`.

The request may carry image bytes in one of two ways:
- `multipart/form-data` with exactly one file part containing the image bytes.
- A `source_url` form field pointing to an HTTPS-accessible image. If the URL targets an Azure blob store for which the tenant has a configured SAS token, the image is referenced in place rather than copied; otherwise the bytes are fetched and stored in the tenant's media storage.

Additional fields on the request body (e.g. `external_media_id`, `meta_tags`, `domain_unit`, `media_timestamp`, `filename`, `custom_data`, `force_set`, `parent_media_id`, `frame`, `trigger_id`, `sequence_ix`) are persisted as media metadata. See `MediaSchema` for the full set.

GIF and AVI uploads are rejected. Multi-file requests are rejected. Empty bodies are rejected. Tenants configured with a media storage quota may receive a quota-exceeded error.

**Auth:** Bearer JWT required

**Request body:** `multipart/form-data` carrying a single file part, or form fields including `source_url`. Other [MediaSchema](#schema-mediaschema) fields may accompany the upload.

**Response:** [MediaSchema](#schema-mediaschema) — the newly persisted media record, including the assigned `media_id` and any derived metadata (dimensions, format, MD5, download URLs).

**Errors:**
- `400` — empty body, invalid `source_url`, or schema validation failure.
- `401` — missing or invalid `Authorization` header.
- `403` — tenant quota exceeded, or Azure source authentication failed.
- `411` — more than one file part supplied.
- `415` — unsupported media format (e.g. GIF, AVI).
- `504` — timeout creating the media record; retry safe.

### `POST /1/media/{media_id}`

**Update existing media metadata**

Update mutable metadata on a previously-uploaded media item. Only fields supplied in the request body are modified. Request bodies must not include a file part — to replace image bytes, delete the media and re-upload.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `media_id` | string | The media identifier returned at upload time. |

**Request body:** `application/json` or form-encoded subset of [MediaSchema](#schema-mediaschema) load-only fields.

**Response:** [MediaSchema](#schema-mediaschema) — the updated media record.

**Errors:**
- `400` — file part present in body, or schema validation failure.
- `403` — media does not belong to the caller's tenant.
- `404` — media not found.
- `504` — timeout updating the record; retry safe.

### `GET /1/media/{media_id}`

**Get media metadata**

Return the metadata record for a single media item, including dimensions, format, MD5 hash, upload metadata, and download URLs.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `media_id` | string | The media identifier returned at upload time. |

**Response:** [MediaSchema](#schema-mediaschema)

**Errors:**
- `403` — media does not belong to the caller's tenant.
- `404` — media not found.

### `DELETE /1/media/{media_id}`

**Delete media**

Permanently delete a media item and remove all of its subject associations. Returns `204 No Content` on success.

Media derived from a parent (e.g. an extracted video frame) cannot be deleted directly; delete the parent instead.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `media_id` | string | The media identifier to delete. |

**Responses:**
- `204` — media deleted.
- `403` — media does not belong to the caller's tenant.
- `404` — media not found.
- `409` — media is derived from a parent; delete the parent media instead.

### `POST /1/media/{media_id}/share`

**Share media via email**

Send an email containing the specified media image to a list of recipients. Intended for ad-hoc sharing of a single image from the Cogniac UI.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `media_id` | string | The media identifier to share. |

**Request body:** [ShareMediaSchema](#schema-sharemediaschema)

**Responses:**
- `204` — share email submitted.
- `404` — media not found.

### `POST /1/media/resumable`

**Resumable video upload**

Upload a video in chunks using a three-phase protocol. Use this endpoint for video files (and for large media in general).

The phase is selected via the `upload_phase` field:

1. **`start`** — Initiates a new upload session. Requires `filename` and `file_size`; optionally accepts `md5` and the same metadata fields supported by `POST /1/media`. Returns a [VideoUploadResponseSchema](#schema-videouploadresponseschema) carrying `upload_session_id`, the assigned `media_id`, and the server-mandated `chunk_size`.
2. **`transfer`** — Uploads a single chunk. Requires `upload_session_id` and `video_file_chunk_no` (chunk index, starting at 1), with the chunk bytes as a single file part. Each chunk must be no larger than the `chunk_size` returned by the `start` phase. Returns the chunk checksum and number.
3. **`finish`** — Finalizes the upload. Requires `upload_session_id`. The assembled video becomes available under the assigned `media_id`.

GIF and AVI source files are rejected at the `start` phase.

**Auth:** Bearer JWT required

**Request body:** [MediaSchema](#schema-mediaschema) fields plus `upload_phase`, `upload_session_id`, `video_file_chunk_no`, `file_size`. For the `transfer` phase, the chunk bytes are sent as a `multipart/form-data` file part.

**Response:** [VideoUploadResponseSchema](#schema-videouploadresponseschema)

**Errors:**
- `403` — missing required field for the requested phase, or `file_size` exceeds the per-video limit.
- `415` — unsupported source format (e.g. GIF, AVI).
- `422` — invalid `upload_session_id` at `finish` phase.
- `504` — timeout assembling the media record; retry the `finish` phase.

### `GET /1/media/all/search`

**Search media by identifier or hash**

Look up media by a single identifying attribute. Exactly one of `md5`, `filename`, `external_media_id`, or `domain_unit` must be supplied as a query parameter.

The optional `subject_uid` parameter further restricts results to media associated with the given subject. The endpoint paginates via `last_key` and `limit` (default `limit=100` when paginating).

Typical use is round-tripping an `external_media_id` set at upload time back to a Cogniac `media_id`, or de-duplicating by MD5 before re-uploading.

**Auth:** Bearer JWT required

**Query parameters:** [MediaSearchQuery](#schema-mediasearchquery)

**Response:** [MediaSearchResponse](#schema-mediasearchresponse)

**Errors:**
- `400` — zero or more than one filter term supplied.
- `404` — `subject_uid` supplied but the subject does not exist.

### `GET /1/media/download/{media_id}/{key_name}`

**Download media bytes**

Stream the bytes of a media item from object storage. `key_name` identifies which representation to return — the full-size media (typically the same as `media_id`) or one of the named resize variants advertised in the parent media record's `resize_urls`. Resolve URLs from the parent media record rather than constructing them by hand.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `media_id` | string | The media identifier. |
| `key_name` | string | Storage object key identifying the variant to stream. |

**Response:** raw bytes streamed with the storage object's content type.

**Errors:**
- `404` — media not found, or media does not belong to the caller's tenant.

### `GET /1/media/blobstore/{media_id}`

**Download media bytes from Azure blob storage**

Stream the bytes of a media item whose storage backend is Azure Blob Storage. Equivalent to `/1/media/download/{media_id}/{key_name}` for tenants whose media storage is configured for Azure. Resolve the appropriate URL from the parent media record's `media_url` field rather than constructing it by hand.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `media_id` | string | The media identifier. |

**Response:** raw bytes streamed with the storage object's content type.

**Errors:**
- `403` — access to the underlying Azure blob was denied.
- `404` — media not found, or media does not belong to the caller's tenant.

### `GET /1/media/{media_id}/subjects`

**List subject associations for media**

Return every subject-media association attached to the specified media. Subject-media associations carry the subject identifier, a probability in `[0, 1]` reflecting confidence that the subject is associated with the media, the current consensus state, and any application-specific metadata produced by the originating application type (e.g. bounding boxes, masks).

There is no pagination — the number of subjects per media item is expected to be small.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `media_id` | string | The media identifier. |

**Query parameters:**

| Name | Type | Description |
|---|---|---|
| `abridged_media` | boolean | If `true`, embedded media objects are reduced to `{media_id}` only. Default `false`. |

**Response fields:**
- `data` — list of [SubjectMediaSearchResults](#schema-subjectmediasearchresults) entries. Each entry carries the embedded `media` object (or its abridged form), a `media_list` of all media referenced by the association (the primary plus any related media for `same`-type app data), and the `subject` association itself.

Consensus values:
- `'True'` — consensus reached that the subject is associated with the media (positive training example).
- `'False'` — consensus reached that the subject is not associated with the media (negative training example).
- `null` — insufficient evidence for consensus.

Some application types only produce `'True'` or `null`.

**Errors:**
- `403` — media does not belong to the caller's tenant.
- `404` — media not found.

### `POST /1/media/{media_id}/detections`

**Submit externally-computed detections for media**

Record detections (inferences or feedback) that were produced outside of Cogniac cloud inference — for example, by an EdgeFlow appliance or a gateway forwarding results from a local model. The endpoint accepts the detections without re-running inference in the cloud.

The request body is an `AppAssertionSchema` envelope containing a list of detections under the `assertions` (or `detections`) key. Each detection follows [DetectionSchema](#schema-detectionschema) and must identify the originating `app_id`, the `subject_uid` it asserts, an uncalibrated probability (`uncal_prob` in `[0, 1]`), the application-specific `app_data_type` and `app_data` (geometry, masks, etc.), and optionally a `focus` (e.g. a bounding box or region of interest within a parent image).

Submitted detections are routed to the appropriate application processing pipeline. Detections with the legacy `app_data_type` value `custom` are silently dropped.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `media_id` | string | The media identifier the detections refer to. |

**Request body:** [AppAssertionSchema](#schema-appassertionschema)

**Responses:**
- `202` — detections accepted for processing.
- `404` — media not found, or detection body failed validation.

### `GET /1/media/{media_id}/detections`

**List detections and history for media**

Return the full detection history for a media item. Each detection represents either a model prediction, user feedback, or an authoritative subject capture (e.g. one written via `POST /1/subjects/{subject_uid}/media`).

This endpoint is intended for drill-down inspection of how subject-media probabilities evolved over time; it is not a streaming or polling interface for new inference output.

If `wait_capture_id` is supplied, the response blocks until the named capture operation completes (or a server-side timeout elapses). When the capture timeout expires the partial result is returned with status `504`.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `media_id` | string | The media identifier. |

**Query parameters:** [MediaDetectionRequest](#schema-mediadetectionrequest)

**Response:** [MediaDetectionSchema](#schema-mediadetectionschema)-shaped object containing `media_list`, `other_media`, `detections` (each carrying `detection_id`, `media_id`, `subject_uid`, optional `user_id`/`model_id`/`app_id`, `uncal_prob`, `created_at`, `prev_prob`, `probability`, optional `app_data_type`/`app_data`). For `area_mask` / `area_mask_set` application types, the response embeds the area-mask PNG bytes as a base64-encoded string under `area_mask_png`.

**Errors:**
- `403` — media does not belong to the caller's tenant.
- `404` — media not found.
- `504` — `wait_capture_id` supplied and the capture operation timed out before completing; partial detections are returned in the response body.
