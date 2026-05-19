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

# GET /1/tenants/<tenant_id>/audit_log?limit=50
resp = cc._get(f"/tenants/{cc.tenant_id}/audit_log", params={"limit": 50})
for entry in resp.json()["data"]:
    print(entry["timestamp"], entry["action"])

# POST /1/applications/<id>/some_custom_action
resp = cc._post(f"/applications/{app_id}/some_custom_action",
                json={"param": "value"})
result = resp.json()

# Hit a non-/1 versioned endpoint
resp = cc._get(f"/22/applications/{app_id}/evaluation_metrics")
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

### Status Subsystems
`model_detections*` (per-app stats), `gpus` (GPU utilization/temp), `upload` (queue stats), `ifconfig` (network), `ping`

## CogniacNetworkCamera

### Key Fields
`network_camera_id`, `camera_name`, `url`, `active`, `description`, `lat`, `lon`

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
