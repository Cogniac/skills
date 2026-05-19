# Cogniac Python SDK Reference

## CogniacConnection

Entry point for all API interaction. Reads auth from env vars or constructor args.

```python
from cogniac import CogniacConnection

cc = CogniacConnection()  # reads COG_API_KEY or COG_USER/COG_PASS, COG_TENANT, COG_URL_PREFIX
cc = CogniacConnection(username="user@example.com", password="pass", tenant_id="abc123")
cc = CogniacConnection(api_key="key", tenant_id="abc123")
```

### Properties
- `cc.tenant` — CogniacTenant object
- `cc.user` — CogniacUser object
- `cc.tenant_id` — current tenant ID
- `cc.url_prefix` — API endpoint URL

### Methods
- `cc.get_all_applications()` — returns list of CogniacApplication
- `cc.get_application(application_id)` — returns CogniacApplication
- `cc.create_application(name, application_type, ...)` — returns CogniacApplication
- `cc.get_all_subjects(public_read=False, public_write=False)` — returns list of CogniacSubject
- `cc.get_subject(subject_uid)` — returns CogniacSubject
- `cc.search_subjects(ids=[], prefix=None, similar=None, name=None, limit=10)` — returns list
- `cc.create_subject(name, description=None, external_id=None)` — returns CogniacSubject
- `cc.get_media(media_id)` — returns CogniacMedia
- `cc.search_media(md5=None, filename=None, external_media_id=None, domain_unit=None, limit=None)` — returns list
- `cc.create_media(filename, meta_tags=None, external_media_id=None, domain_unit=None, ...)` — returns CogniacMedia
- `cc.get_all_edgeflows()` — returns list of CogniacEdgeFlow
- `cc.get_edgeflow(edgeflow_id)` — returns CogniacEdgeFlow
- `cc.get_all_cameras()` — returns list of CogniacNetworkCamera
- `cc.get_camera(network_camera_id)` — returns CogniacNetworkCamera
- `cc.get_version(auth=False)` — returns dict with API version info
- `CogniacConnection.get_all_authorized_tenants(username, password, url_prefix)` — classmethod, returns tenant list

## Calling arbitrary API endpoints

When you need an endpoint the SDK doesn't wrap (anything documented in `references/api/` but not listed above), use the connection's low-level HTTP methods. They are named with a leading underscore by Python convention, but the SDK uses them internally as the canonical way to hit any endpoint — they handle auth, re-auth on credential expiry, the `/1/` version prefix, the `url_prefix`, and retries:

```python
cc._get(path, params=None, timeout=None, **kwargs)      # returns httpx.Response
cc._post(path, json=..., data=..., files=..., **kwargs)
cc._delete(path, json=..., **kwargs)
cc._head(path, **kwargs)
```

- `path` may be a bare path like `"/applications/<id>/feedback"` — the connection prepends `/1` if no `/<version>` prefix is present, then prepends `cc.url_prefix`. Pass an explicit version (`"/22/applications/..."`) when the endpoint lives under a non-`/1` API version. Pass a full `http(s)://...` URL to bypass prefixing entirely.
- The response is a raw `httpx.Response`. Call `.json()` for JSON bodies, `.content`/`.iter_bytes()` for binary.
- `4xx`/`5xx` are converted to `ClientError`/`ServerError` before returning (import: `from cogniac import ClientError, ServerError, CredentialError`); `401` becomes `CredentialError` and triggers one transparent re-auth + retry.

### Example: an endpoint the SDK doesn't expose

```python
from cogniac import CogniacConnection
cc = CogniacConnection()

# GET — a non-/1 versioned endpoint the SDK doesn't wrap.
# From references/api/evaluation-metrics-api.md:
#   GET /22/schemas/evaluation_metrics
# Returns the JSON Schema for every supported evaluation-metric type
# (box_F1, segmentation_IoU, point_count_F1, …). No IDs to look up.
resp = cc._get("/22/schemas/evaluation_metrics")
for metric_name, schema in resp.json().items():
    print(metric_name, "→", schema.get("title", ""))

# POST — attach a short message to a media item.
# From references/api/message-core-api.md:
#   POST /1/messages
resp = cc._post("/messages", json={
    "media_id": media_id,
    "message": "flagged for re-review",
})
message_id = resp.json()["message_id"]
```

### Finding the right path

`references/api/<service>.md` lists every endpoint with its HTTP verb, path, request/response schema, and required roles. Translate directly:

| API doc says                              | SDK call                                                |
|-------------------------------------------|---------------------------------------------------------|
| `GET /1/applications/{id}/feedback`       | `cc._get(f"/applications/{id}/feedback")`               |
| `POST /1/subjects` with JSON body         | `cc._post("/subjects", json={...})`                     |
| `DELETE /1/media/{id}`                    | `cc._delete(f"/media/{id}")`                            |
| `GET /22/applications/{id}/...`           | `cc._get(f"/22/applications/{id}/...")` (explicit ver)  |

Prefer a wrapped method (`cc.get_application(id)`, `app.get_feedback()`, etc.) when one exists — it returns typed objects rather than raw JSON. Drop down to `_get`/`_post` only for endpoints the SDK doesn't cover.

## CogniacApplication

### Key Fields
`application_id`, `name`, `type`, `description`, `active`, `input_subjects`, `output_subjects`, `app_managers`, `app_type_config`, `created_at`, `created_by`

### Methods
- `app.detections(start=None, end=None, reverse=True, probability_lower=None, probability_upper=None, limit=None, consensus_none=False)` — yields detection dicts
- `app.models(start=None, end=None, limit=None, reverse=True)` — yields released model dicts
- `app.model_name()` — returns name of current best model
- `app.download_model(model_id=None)` — downloads model file
- `app.pending_feedback()` — returns count of pending feedback
- `app.get_feedback(limit=10)` — returns feedback request messages
- `app.post_feedback(media_id, subjects)` — submit feedback
- `app.usage(start, end)` — yields usage records
- `app.accumulate_usage(start, end)` — returns cumulative usage
- `app.evaluation_metrics()` — returns list of active evaluation metric configs (each with `evaluation_metric_hash`, `primary`/`active` flags, and the metric body — name, detection thresholds, subject weights, tolerances)
- `app.leaderboard(set_assignment='validation', snapshot_type='regular', eval_metrics='primary')` — returns the most recent ranked-candidate-model snapshot dict (`snapshot` is the ranked list with rank, F1, precision/recall, TP/FP/FN per model). `set_assignment` ∈ {`validation`,`training`}; `snapshot_type` ∈ {`regular`,`int8`}; `eval_metrics` ∈ {`primary`,`all`}. Returns `{'message': ...}` if no snapshot exists yet.
- `app.add_input_subject(subject)` / `app.add_output_subject(subject)` — wire a subject into the app's pipeline
- `app.delete()` — delete the application

**Attribute assignment triggers updates.** Assigning to most fields on a `CogniacApplication` object automatically POSTs the change to the API — no separate `.save()` or `.update()` call needed. Common patterns:

```python
app.active = False                          # deactivate
app.input_subjects = ["uid1", "uid2"]       # replace full input list
app.output_subjects = ["uid3"]              # replace full output list
app.name = "New Name"
```

> **This pattern applies across SDK objects** — `CogniacSubject`, `CogniacMedia`, and others also trigger API updates on field assignment.
>
> **Setting attributes that don't exist yet is fine.** If the object was fetched without a field (e.g. a subject with no `custom_data`), the attribute won't be present locally — but assigning to it still works and POSTs the value to the API:
> ```python
> subject.custom_data = '{"note": "re-review"}'  # works even if subject.custom_data didn't exist
> ```

## CogniacSubject

### Key Fields
`subject_uid`, `name`, `description`, `external_id`, `public_read`, `public_write`, `created_at`, `created_by`

### Methods
- `subject.media_associations(start=None, end=None, reverse=True, probability_lower=None, probability_upper=None, consensus=None, sort_probability=False, limit=None)` — yields association dicts
- `subject.associate_media(media, focus=None, consensus='None', probability=None, force_feedback=False)` — associate media with subject
- `subject.disassociate_media(media, focus=None)` — remove association
- `subject.create_reference_media(filename, ...)` — upload reference media
- `subject.delete()` — delete subject

### Media Association Dict Fields
`media_id`, `subject_uid`, `probability` (0-1), `consensus` ('True'/'False'/'Sidelined'/None), `timestamp`, `focus`, `app_data_type`, `app_data`

## CogniacMedia

### Key Fields
`media_id`, `filename`, `media_format`, `image_width`, `image_height`, `size`, `hash` (MD5), `status`, `media_url`, `external_media_id`, `domain_unit`, `meta_tags`, `custom_data`, `created_at`

### Methods
- `media.detections(wait_capture_id=None)` — returns detection list
- `media.subjects()` — returns associated subjects
- `media.download(filep=None, timeout=60)` — download media file
- `media.delete()` — delete media

## CogniacTenant

### Key Fields
`tenant_id`, `name`, `description`, `region`, `created_at`

### Methods
- `tenant.users()` — returns user list
- `tenant.usage(start, end, period='15min')` — yields usage records
- `tenant.add_user(user_email, role='tenant_user')` — add user
- `tenant.delete_user(user_email)` — remove user
- `tenant.set_user_role(user_email, role)` — change user role

## CogniacEdgeFlow

### Key Fields
`gateway_id`, `name`, `model`, `description`

### Methods
- `ef.status(subsystem_name=None, start=None, end=None, reverse=True, limit=None)` — yields status events
- `ef.get_aggregated_stats(start=None, end=None)` — returns detection/pixel counts
- `ef.process_media(subject_uid, filename, ...)` — upload media for edge processing
- `ef.trigger_camera_capture(subject_uid, trigger_domain_unit=None)` — trigger camera
- `ef.ping(ping_id=None)` — ping device
- `ef.get_version()` — get EdgeFlow software version
- `ef.time_bound_media_upload(start_time, end_time)` — request the device to upload images captured in a time window back to CloudCore
- `ef.flush_upload_queue(start_time=None, end_time=None)` — flush the device-to-CloudCore upload queue (optionally bounded to a time window)
- `ef.reboot()` — reboot the EdgeFlow
- `ef.upgrade(software_version)` — upgrade the EdgeFlow to a specific software version
- `ef.set_boot_software_version(software_version)` — set the boot/target software version without an immediate upgrade
- `ef.factory_reset()` — factory-reset the EdgeFlow (also deletes the EdgeFlow record in CloudCore/SiteCore)

### Status Subsystems
`model_detections*` (per-app stats), `gpus` (GPU utilization/temp), `upload` (queue stats), `ifconfig` (network), `ping`

## CogniacNetworkCamera

### Key Fields
`network_camera_id`, `camera_name`, `url`, `active`, `description`, `lat`, `lon`

### Methods
- `camera.update(url=None, camera_name=None, ...)` — patch camera fields
- `camera.delete()` — delete the camera

## CogniacUser

Returned by `cc.user`. Exposes the calling user's API-key management.

### Methods
- `user.api_keys()` — list the user's API keys
- `user.api_key(key_id)` — fetch a specific API key
- `user.create_api_key(description)` — create a new API key
- `user.delete_api_key(key_id)` — revoke an API key

## CogniacOpsReview

Operations-review queue: a tenant-wide work queue where items (typically media-with-context payloads) are added for human review and reviewers post pass/fail-style results. Distinct from the labeling feedback queue.

### Classmethods (factories)
- `CogniacOpsReview.create(connection, review_items, review_unit=None)` — enqueue a new review item
- `CogniacOpsReview.get(connection)` — pop a single pending item from the queue
- `CogniacOpsReview.get_pending(connection)` — return the count of pending items
- `CogniacOpsReview.create_result(connection, review_id, result, comment=None)` — record a reviewer decision for an item
- `CogniacOpsReview.search(connection, review_unit=None, media_id=None, external_media_id=None, result=None, ...)` — search reviews by media/unit/result; yields paginated results

### Methods
- `review.delete()` — delete the review item

## CogniacExternalResult

Records produced by external (non-Cogniac) systems that are attached to media or to a customer-defined `domain_unit` (e.g., a serial number) for later cross-reference. Useful for closing the loop between Cogniac inference output and downstream system decisions.

### Classmethods (factories)
- `CogniacExternalResult.create(connection, result_type, result, media_id=None, domain_unit=None)` — record an external result
- `CogniacExternalResult.get(connection, external_result_id)` — fetch a single record
- `CogniacExternalResult.search(connection, media_id=None, domain_unit=None, time_start=None, time_end=None, reverse=True, limit=None)` — search by media, domain unit, or time window

### Methods
- `result.delete()` — delete the external result

## Error Classes
- `CredentialError` (401) — invalid credentials, triggers re-auth
- `ServerError` (5xx) — retryable with exponential backoff
- `ClientError` (4xx) — not retried

## Environment Variables
| Variable | Purpose | Default |
|----------|---------|---------|
| `COG_API_KEY` | API key auth | — |
| `COG_USER` | Username (email) | — |
| `COG_PASS` | Password | — |
| `COG_TENANT` | Tenant ID | — |
| `COG_URL_PREFIX` | API endpoint | `https://api.cogniac.io` |
