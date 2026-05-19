# tenant-core-api

Manages Cogniac tenants — the top-level customer organization in the platform. A tenant owns users, applications, network cameras, subjects, and integration configuration (EdgeFlow TLS certificates, Meraki credentials). The endpoints in this service support tenant administrator workflows: creating a tenant, inviting and managing users, browsing tenant resources, and configuring EdgeFlow and Meraki integrations.

All endpoints require Bearer JWT authentication unless explicitly noted. With the exception of tenant creation, callers are restricted to the tenant encoded in their JWT — requests against another tenant return `404`.

## Endpoints

### `POST /1/tenants`

**Creates a new tenant**

Creates a new tenant object, assigns it a unique identifier `tenant_id`,
and adds the user which created this tenant to the tenant's admin group.

The request body accepts a partial [TenantSchema](#schema-tenantschema). `name` is the only effectively required field. The response is a [TenantSchema](#schema-tenantschema) for the newly created tenant.

**Auth:** Bearer JWT; required roles: `{cogniac_support, meraki_admin, tenant_creator}`

### `POST /1/tenants/{id}`

**Update tenant details**

Updates the calling user's tenant. The `id` path parameter must match the tenant encoded in the JWT (the literal value `current` is also accepted but is deprecated). The request body is a partial [TenantSchema](#schema-tenantschema); only the supplied fields are modified.

If `meraki_dashboard_api_key` or `meraki_api_host` is included and Meraki integration is enabled, the key is validated against the Meraki API before being persisted.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target tenant ID. Must match the caller's tenant. |

### `DELETE /1/tenants/{id}`

**Delete tenant**

Permanently deletes the caller's tenant. The tenant must have no remaining applications or subjects; otherwise the request is rejected with `403`. Any EdgeFlow TLS material associated with the tenant is removed as part of the delete.

**Auth:** Bearer JWT; required roles: `{tenant_admin}`

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target tenant ID. Must match the caller's tenant. |

### `POST /1/tenants/{id}/users`

**Add a user to a tenant**

Adds an existing user to the tenant or, when `machine_user` is `true`, creates a new machine user and adds it to the tenant in a single operation. Machine users have no password and authenticate exclusively via the API key returned in the response — this is the only opportunity to retrieve that key.

The request body is a [CreateTenantUserSchema](#schema-createtenantuserschema); when creating a machine user, fields from [UserSchema](#schema-userschema) (notably `email`, `given_name`, `surname`) are also accepted to populate the user record. The response is a [CreateTenantUserResponseSchema](#schema-createtenantuserresponseschema).

Adding an existing human user requires the `tenant_admin` role. A `tenant_user` may create a machine user with the `ef_device` role.

**Auth:** Bearer JWT; required roles: `{tenant_admin}` (a caller with the `tenant_user` role may alternatively create a machine user with the `ef_device` role)

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target tenant ID. Must match the caller's tenant. |

### `DELETE /1/tenants/{id}/users`

**Removes a user from a tenant**

Removes the user identified by `user_id` (supplied in the request body as a [TenantUserSchema](#schema-tenantuserschema)) from the tenant. A non-admin user may remove only their own membership; `tenant_admin` is required to remove any other user.

Returns `204 No Content` on success.

**Auth:** Bearer JWT; required roles: `{tenant_admin}`

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target tenant ID. Must match the caller's tenant. |

### `POST /1/tenants/{tenant_id}/users/role`

**Update's a tenant user's role for the tenant**

Changes the tenant role of an existing human (non-machine) user within the tenant. The request body must supply `user_id` and `role`, where `role` is one of the valid tenant roles (e.g. `tenant_admin`, `tenant_user`). Machine user roles cannot be changed through this endpoint.

Returns `204 No Content` on success.

**Auth:** Bearer JWT; required roles: `{tenant_admin}`

**Path params:**

| Name | Type | Description |
|---|---|---|
| `tenant_id` | string | Target tenant ID. Must match the caller's tenant. |

### `GET /1/tenants/{id}/applications`

**Lists applications for a tenant**

Returns the active applications in the caller's tenant, sorted by name. The response is a `{"data": [...]}` envelope of [ApplicationSchema](#schema-applicationschema) objects, with an optional top-level `last_key` when paginating.

Accepts query parameters from [ApplicationsQuerySchema](#schema-applicationsqueryschema): `reverse` to invert the sort order; `limit` and `last_key` for paginated retrieval; `config_only` to receive only the static configuration fields and skip runtime/model state; and `f` to restrict the response to a specific subset of fields.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target tenant ID. Must match the caller's tenant. |

### `GET /1/tenants/{id}/networkCameras`

**Tenants Network Cameras**

Lists all network cameras registered to the caller's tenant. The response is a `{"data": [...]}` envelope of [NetworkCameraSchema](#schema-networkcameraschema) objects sorted by `camera_name`. Pass `reverse=true` to invert the sort order.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target tenant ID. Must match the caller's tenant. |

### `GET /1/tenants/{id}/invites`

**Returns a list of "pending" invitations for the tenant associated with**

the requesting user (as encoded in the JWT token).

By default only invitations in the `pending` state are returned. Pass `invitation_status` to filter by a specific state, or `invitation_status=all` to include every state except `deleted`. The response is a list of [InvitationSchema](#schema-invitationschema) objects.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target tenant ID. Must match the caller's tenant. |

### `POST /1/tenants/{id}/invites`

**Invite a user to the tenant**

Note that we require a token with a valid tenant.  The tenant identifier
encoded as a route parameter in the URI string is deprecated in favor
of the tenant identifier associated with the token and can be safely
ignored _for this request_.

The request body is an [InvitationSchema](#schema-invitationschema). `invited_user_email` identifies the invitee; `role` sets the initial tenant role they will receive on acceptance (defaults to `tenant_user`); `realm_id` optionally overrides the identity provider the invited user will authenticate against. If an invitation for the same email and tenant is already pending, the existing record is returned unchanged.

An invitation email is sent to the invitee with an `invitation_url` that they follow to accept or, for new users, register a Cogniac account.

**Auth:** Bearer JWT; required roles: `{tenant_admin}`

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target tenant ID. Must match the caller's tenant. |

### `DELETE /1/tenants/{id}/invites`

**Deletes a membership invitation for a tenant**

Marks a pending invitation for the tenant as deleted. The request body must identify the invitee by `invited_user_email` (as an [InvitationSchema](#schema-invitationschema)). Returns `204 No Content` on success.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target tenant ID. Must match the caller's tenant. |

### `GET /1/tenants/{tenant_id}/import/{cloudcore_import_key}`

**Get CloudCore import key JSON file for a tenant**

Returns the CloudCore import bundle as a JSON document. Used by EdgeFlow/CloudFlow appliances during onboarding to retrieve the configuration needed to bind to their owning tenant. The `cloudcore_import_key` is a per-tenant secret issued by Cogniac and must be protected accordingly.

**Auth:** no auth required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `tenant_id` | string | Target tenant ID. |
| `cloudcore_import_key` | string | Per-tenant import token issued by Cogniac. Treat as a secret. |

### `POST /1/tenants/{id}/edgeflow_certificate`

**Sets a new TLS Certificate on an Edgeflow Gateway**

Uploads a new TLS key/certificate pair to be used by the tenant's EdgeFlow gateways. The request body is a [TLSCertKeyPairSchema](#schema-tlscertkeypairschema) carrying PEM-encoded `cert` (a leaf-to-root chain) and matching `key`.

The submission is rejected if any of the following hold: the private key fails consistency validation; the certificate chain cannot be parsed; the leaf certificate is already expired or not yet valid; the leaf certificate expires in less than three weeks; the leaf certificate has no Common Name; or the private key does not match the leaf certificate.

**Auth:** Bearer JWT; required roles: `{tenant_admin}`

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target tenant ID. Must match the caller's tenant. |

### `GET /1/tenants/{id}/edgeflow_certificate`

**Get the existing TLS Certificate Metadata from an Edgeflow Gateway**

Returns metadata describing the tenant's installed EdgeFlow TLS certificate (issuer, validity window, fingerprint, domain name, algorithm) along with the PEM-encoded certificate itself. The private key is never returned. Responds `404` if no certificate is installed.

**Auth:** Bearer JWT; required roles: `{tenant_admin}`

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target tenant ID. Must match the caller's tenant. |

### `DELETE /1/tenants/{id}/edgeflow_certificate`

**Deletes the existing TLS Certificate from an Edgeflow Gateway**

Removes the tenant's EdgeFlow TLS certificate and private key along with their metadata.

**Auth:** Bearer JWT; required roles: `{tenant_admin}`

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target tenant ID. Must match the caller's tenant. |

### `DELETE /1/tenants/{id}/meraki_api_key`

**Deactivate any Meraki camera capture apps and delete output_subjects**

from those apps.
On the Meraki side delete camera tags used in 'meraki_camera_capture'
apps and any camera tags in downstream apps.
Delete the tenant's meraki_dashboard_api_key.

Use this endpoint to fully unwind a tenant's Meraki integration. The tenant must currently have a working Meraki integration (the stored API key is validated against Meraki before any cleanup begins). Returns `204 No Content` on success.

**Auth:** Bearer JWT; required roles: `{tenant_admin}`

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target tenant ID. Must match the caller's tenant. |

## Schemas

### `ApiKeySchema` <a id='schema-apikeyschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `key_id` | string | no |  | Public identifier of the API key. |
| `user_id` | string | no |  | ID of the user the key is provisioned for. |
| `email` | string | no |  | Email of the user the key is provisioned for. |
| `last_auth` | integer | no |  | Unix timestamp of the most recent authentication using this key. |
| `created_at` | integer | no |  | Unix timestamp at which the key was created. |
| `description` | string | no |  | Free-form description of the key's purpose. |
| `api_key` | string | no |  | Full `key_id:secret` credential. Returned only at key creation time and never again. |

### `TrainingSummarySchema` <a id='schema-trainingsummaryschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `training_in_progress` | integer | no | default=0 | Number of training jobs currently in progress for the application. |

### `UsageMetricsMediaInfoSchema` <a id='schema-usagemetricsmediainfoschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `media_id` | string | no |  | Identifier of the referenced media item. |
| `area` | integer | no |  | Media area in pixels. |
| `width` | integer | no |  | Media width in pixels. |
| `height` | integer | no |  | Media height in pixels. |

### `RuntimePolicySchema` <a id='schema-runtimepolicyschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `gpu_selection_policy` | string | no | one of {'instance-ix', 'by-free-memory'} | Strategy for assigning the application's inference to a GPU. |
| `gpu_simul_load` | integer | no |  | Maximum number of models permitted to share the selected GPU concurrently. |
| `model_load_policy` | string | no | one of {'timebound', 'run-to-completion', 'realtime'} | Policy for scheduling the loaded model's execution. |
| `model_seconds` | integer | no |  | Time budget for `timebound` execution. |
| `rtc_timeout_seconds` | number | no |  | Timeout for `realtime` execution. |

### `ApplicationInferenceExecutionPolicySchema` <a id='schema-applicationinferenceexecutionpolicyschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `runtime_policy` | [RuntimePolicySchema](#schema-runtimepolicyschema) | no |  | GPU and model scheduling policy. |
| `max_batch` | integer | no |  | Maximum batch size for inference. |
| `replicas` | integer | no |  | Number of inference replicas to run. |

### `ApplicationSchema` <a id='schema-applicationschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `application_id` | string | no |  | Unique application identifier. |
| `name` | string \| null | no |  | Human-readable application name. |
| `description` | string \| null | no | default=None | Free-form description of the application. |
| `app_type` | string \| null | no |  | Application type (e.g. `classification`, `box_detection`). |
| `created_by` | string | no |  | Email of the user who created the application. |
| `tenant_id` | string | no |  | Identifier of the owning tenant. |
| `input_subjects` | list[any] \| null | no |  | Subjects whose media feeds this application. |
| `output_subjects` | list[any] \| null | no |  | Subjects to which the application publishes results. |
| `created_at` | number | no | range(min=0) | Unix timestamp at creation. |
| `modified_at` | number | no | range(min=0) | Unix timestamp of the most recent modification. |
| `active` | boolean | no | default=True | Whether the application is currently active. |
| `realtime` | boolean \| null | no | default=False | Whether the application runs in realtime mode. |
| `release_metrics` | string \| null | no |  | Identifier of the metric set used to gate model releases. |
| `detection_thresholds` | any \| null | no |  | Per-subject detection thresholds. |
| `subject_weights` | any \| null | no |  | Per-subject training weights. |
| `detection_post_urls` | list[any] \| null | no |  | URLs to POST detection results to. |
| `input_threshold` | number \| null | no | default=None; range(min=0, max=1) | Minimum upstream detection probability required to admit media for processing. |
| `override_upstream_detection_filter` | boolean \| null | no | default=False | Disables the default upstream-detection input filter. |
| `drop_input_focus` | boolean \| null | no | default=False | Drops focus-region context from upstream detections before processing. |
| `gateway_post_urls` | list[any] \| null | no |  | URLs to which the EdgeFlow gateway POSTs results. |
| `current_performance` | number | no | default=None; range(min=0, max=1) | Most recent overall performance score for the current release model. |
| `gpu_memory_gigabytes` | number | no | default=None; range(min=0) | GPU memory footprint of the application's release model. |
| `gpu_throughput_megapixels_per_second` | number | no | default=None; range(min=0) | Current observed GPU throughput in megapixels/second. |
| `max_gpu_throughput_megapixels_per_second` | number | no | default=None; range(min=0) | Peak measured GPU throughput in megapixels/second. |
| `model_initialization_time_seconds` | number | no | default=None; range(min=0) | Time required to initialize the release model. |
| `max_media_info` | [UsageMetricsMediaInfoSchema](#schema-usagemetricsmediainfoschema) | no |  | Dimensions of the largest media seen by the application. |
| `replay` | boolean \| null | no | default=False | Whether the application is in replay mode. |
| `last_candidate_at` | number | no | default=None | Unix timestamp of the most recent candidate model. |
| `last_released_at` | number | no | default=None | Unix timestamp of the most recent model release. |
| `last_eval_time` | number | no | default=None | Unix timestamp of the most recent evaluation. |
| `candidate_model_count` | integer | no | default=None | Number of candidate models on record. |
| `model_id` | string | no | default=None | Identifier of the currently released model. |
| `model_image_id` | string | no | default=None | Container image identifier for the released model. |
| `model_runtime_image` | string | no | default=None | Runtime image used to serve the released model. |
| `release_model_count` | integer | no | default=None | Number of release models on record. |
| `training_data_count` | integer | no | default=None | Number of training items associated with the application. |
| `training_summary` | [TrainingSummarySchema](#schema-trainingsummaryschema) | no |  | Summary of in-progress training activity. |
| `validation_data_count` | integer | no | default=None | Number of validation items associated with the application. |
| `consensus_release_id` | string | no | default=None | Identifier of the consensus model release in effect. |
| `consensus_release_timestamp` | string | no | default=None | Timestamp of the consensus release. |
| `requested_feedback_per_hour` | integer \| null | no |  | User-requested feedback rate target. |
| `system_feedback_per_hour` | integer | no |  | System-derived feedback rate. |
| `hpo_credit` | integer \| null | no | default=0; range(min=0, max=50) | Hyperparameter optimization credits allocated to this application. |
| `output_subjects_external_ids` | any \| null | no |  | External identifiers for the application's output subjects. |
| `app_managers` | list[any] \| null | no |  | Emails of users designated as managers of this application. |
| `detection_post_line_users` | list[any] \| null | no |  | LINE user identifiers to notify with detection results. |
| `app_type_config` | any | no |  | Application-type-specific configuration block. |
| `app_type_status` | any | no | default=None | Application-type-specific status block. |
| `custom_data` | any \| null | no |  | Caller-supplied opaque metadata associated with the application. |
| `max_inference_megapixels` | integer \| null | no | default=None | Upper bound on per-frame inference work, in megapixels. |
| `input_queue_count` | integer | no |  | Depth of the application's input queue. |
| `feedback_resample_ratio` | number | no | default=None; range(min=0, max=1) | Probability with which previously seen feedback is resampled. |
| `production_gateway_model_id` | string | no |  | Model id currently deployed to production EdgeFlow/CloudFlow gateways for this application. |
| `staging_gateway_model_id` | string | no |  | Model id currently deployed to staging gateways for this application. |
| `edgeflow_upload_policies` | list[any] | no |  | EdgeFlow upload-policy specifications attached to this application. |
| `inference_execution_policies` | [ApplicationInferenceExecutionPolicySchema](#schema-applicationinferenceexecutionpolicyschema) | no |  | Relevant only for model-based apps. |
| `evaluation_metrics` | list[object] | no |  | evaluation metrics |
| `custom_fields` | any \| null | no |  | <PENDING_DEPRECATION> |
| `refresh_feedback` | boolean \| null | no | default=False | <DEPRECATED> |

### `ApplicationsQuerySchema` <a id='schema-applicationsqueryschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `reverse` | boolean | no | default=False | Reverses the default sort order of the response. |
| `last_key` | string \| null | no |  | Pagination. |
| `limit` | integer \| null | no |  | Maximum number of items to return per page. |
| `config_only` | boolean | no | default=False | Excludes fields with external dependencies. |
| `f` | list[any] \| null | no |  | List of requested field names |

### `TLSCertKeyPairSchema` <a id='schema-tlscertkeypairschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `key` | string | **yes** |  | PEM-encoded private key matching the leaf certificate. |
| `cert` | string | **yes** |  | PEM-encoded certificate chain ordered leaf-first. |

### `EdgeFlowTLSCertInfoSchema` <a id='schema-edgeflowtlscertinfoschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `valid_beginning` | number | no | default=None | Unix timestamp from which the certificate is valid. |
| `expires` | number | no | default=None | Unix timestamp at which the certificate expires. |
| `algorithm` | string | no | default=None | Signature algorithm of the certificate. |
| `issuer` | string | no | default=None | Certificate issuer distinguished name. |
| `serial_number` | string | no | default=None | Certificate serial number. |
| `fingerprint` | string | no | default=None | SHA-256 fingerprint of the certificate. |
| `domain_name` | string | no | default=None | Certificate Common Name. |
| `certificate` | string | no | default=None | PEM-encoded certificate. |

### `InvitationSchema` <a id='schema-invitationschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `invited_user_email` | string (email) | no |  | Email of the invited user. |
| `created_at` | number | no |  | Unix timestamp at which the invitation was issued. |
| `created_by` | string | no |  | Email of the user who issued the invitation. |
| `invitation_status` | string | no | default='pending' | Current invitation state (e.g. `pending`, `accepted`, `declined`, `deleted`). |
| `tenant_id` | string | no |  | Identifier of the tenant the user was invited to. |
| `register_url` | string \| null | no |  | Override base URL embedded in the invitation link for new users. |
| `tenant_name` | string | no |  | Display name of the inviting tenant. |
| `invitation_url` | string | no |  | URL the invitee follows to accept the invitation or register. |
| `accepted_at` | number | no |  | Unix timestamp at which the invitation was accepted. |
| `resend_counter` | integer | no |  | Number of times the invitation email has been resent. |
| `last_resend_at` | number | no |  | Unix timestamp of the most recent resend. |
| `last_resend_by` | string (email) | no |  | Email of the user who last resent the invitation. |
| `code` | string | no |  | Per-invitation token embedded in the invitation URL. |
| `role` | string | no | default='tenant_user' | Invited user's initial tenant role. |
| `realm_id` | string | no | default=None | Indicates the realm to use to authenticate the invited user. If unset or `None`, then the default Cogniac authentication realm will be used. If set, the user will be redirected to the identity provider to authenticate when creating their Cogniac account. |
| `invited_user` | [UserSchema](#schema-userschema) | no | default=None | User information stored when they initiate user creation by accepting a user invitation and their invitation is associated with a third-party identity provider. |

### `NetworkCameraSchema` <a id='schema-networkcameraschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `network_camera_id` | string | no |  | Unique camera identifier. |
| `tenant_id` | string | no |  | Identifier of the owning tenant. |
| `subject_uid` | string | no |  | Identifier of the subject that carries media captured from this camera. |
| `alt_subject_uid` | list[string] | no |  | Additional subjects to which captured media is associated. |
| `created_by` | string | no |  | Email of the user who registered the camera. |
| `url` | string \| null | **yes** | default=None | Camera stream URL. |
| `camera_name` | string \| null | **yes** | default=None | Human-readable camera name. |
| `description` | string \| null | no | default=None | Free-form description of the camera. |
| `active` | boolean \| null | no |  | Whether capture from the camera is enabled. |
| `created_at` | number | no |  | Unix timestamp at registration. |
| `modified_at` | number | no |  | Unix timestamp of most recent modification. |
| `lat` | number \| null | no | default=None | Camera latitude. |
| `lon` | number \| null | no | default=None | Camera longitude. |
| `hae` | number \| null | no | default=None | Camera height above ellipsoid. |
| `discovered_by` | string \| null | no | default=None | Identifier of the gateway that discovered the camera. |
| `gateway_id` | string \| null | no | default=None | <DEPRECATE> NOTE: Deprecate in favor of `discovered_by`. |
| `genicam_xml` | string | no |  | Reference to the camera's GenICam XML description. |
| `genicam_features` | any | no |  | Parsed GenICam feature attributes. |
| `last_pose_change_timestamp` | number | no |  | camera pose and model related parameters approximate time of last camera pose change.  Images before this time were not generated by the current camera pose and the current pose is invalid for computations of images before this timestamp, updated by user |
| `last_model_change_timestamp` | number | no |  | approximate time of last camera model change, updated by user |
| `orientation` | integer \| null | no | default=0 | gige cam rotation - 0, 90, 180, 270 degrees. |
| `resolution_h_px` | integer \| null | no | default=None | camera intrinsic parameters resolution in horizontal/vertical dimension |
| `resolution_v_px` | integer \| null | no | default=None |  |
| `pixel_h_um` | number \| null | no | default=None | pixel (unit cell) horizontal/vertical in micrometers |
| `pixel_v_um` | number \| null | no | default=None |  |
| `focal_length_h_mm` | number \| null | no | default=None | focal length in mm |
| `focal_length_v_mm` | number \| null | no | default=None |  |
| `skew` | number | no | default=0 | skew reflects pixel deviation from a square. Equals zero for good cameras |
| `ch_px` | number \| null | no | default=None | Principal point in terms of pixel dimensions in horizontal/vertical direction. Expected to be at a sensor's center, but precise calibration can provide different estimates |
| `cv_px` | number \| null | no | default=None |  |
| `radial_distortion_coefficients` | list[number] | no |  | radially symmetric distortions arising from the symmetry of a photographic lens |
| `tangential_distortion_coefficients` | list[number] | no |  | tangential distortion caused by physical elements in a lens not being perfectly aligned |
| `pitch` | number \| null | no | default=None | camera pose, yaw, pitch, roll in radians |
| `yaw` | number \| null | no | default=None |  |
| `roll` | number \| null | no | default=None |  |
| `tx_m` | number \| null | no | default=None | translation vector in meters.  (camera location in meters) |
| `ty_m` | number \| null | no | default=None |  |
| `tz_m` | number \| null | no | default=None |  |
| `origin_x` | number \| null | no | default=None | pixel coordinate of the origin, and x, y, z axes |
| `origin_y` | number \| null | no | default=None |  |
| `x_axis_x` | number \| null | no | default=None |  |
| `x_axis_y` | number \| null | no | default=None |  |
| `y_axis_x` | number \| null | no | default=None |  |
| `y_axis_y` | number \| null | no | default=None |  |
| `z_axis_x` | number \| null | no | default=None |  |
| `z_axis_y` | number \| null | no | default=None |  |
| `spec_version_major` | string \| null | no | default=None | camera info reported during camera discovery (e.g., by GigE protocol) |
| `spec_version_minor` | string \| null | no | default=None |  |
| `device_mode` | string \| null | no | default=None |  |
| `IP_config_options` | string \| null | no | default=None |  |
| `IP_config_current` | string \| null | no | default=None |  |
| `current_IP` | string \| null | no | default=None |  |
| `current_subnet_mask` | string \| null | no | default=None |  |
| `default_gateway` | string \| null | no | default=None |  |
| `mac_address` | string \| null | no | default=None |  |
| `model_name` | string \| null | no | default=None |  |
| `serial_number` | string \| null | no | default=None |  |
| `device_version` | string \| null | no | default=None |  |
| `manufacturer_name` | string \| null | no | default=None |  |
| `manufacturer_info` | string \| null | no | default=None |  |
| `user_defined_name` | string \| null | no | default=None |  |
| `gige_features` | list[object] \| null | no |  | GigE Vision feature descriptors reported by the camera. |
| `custom_configuration` | any | no |  | Additional camera configuration. |

### `TenantSchema` <a id='schema-tenantschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `tenant_id` | string | no |  | Unique tenant identifier. |
| `description` | string | no |  | Free-form description of the tenant. |
| `name` | string | no |  | Human-readable tenant name. |
| `created_by` | string | no |  | Email of the user who created the tenant. |
| `created_at` | number | no |  | Unix timestamp at creation. |
| `modified_by` | string \| null | no | default=None | Email of the user who most recently modified the tenant. |
| `modified_at` | number | no |  | Unix timestamp of most recent modification. |
| `custom_data` | any \| null | no |  | Caller-supplied opaque metadata associated with the tenant. |
| `labeling_mask_decoder_model_id` | string \| null | no | default=None | Identifier of the model used to decode labeling masks for this tenant. |
| `password_expiration_days` | integer \| null | no | default=None; range(min=1) | Number of days before a user's password must be rotated. |
| `default_subject_expires_in_months` | number \| null | no | default=None; range(min=0) | Default expiry, in months, applied to newly created subjects in this tenant. |
| `azure_sas_tokens` | object | no |  | See https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview#sas-token. |
| `media_storage_config` | object | no |  | AWS S3 by default. Can configure to use Azure Blob Service. |
| `media_storage_limit_GB` | integer \| null | no | default=None; range(min=0) | Maximum total media storage the tenant may consume, in gigabytes. |
| `notification_config` | object | no |  | Tenant-wide notification destinations (email, webhook). |
| `has_ops` | boolean | no |  | Whether the tenant has an operations integration enabled. |
| `meraki_integration` | boolean | no | default=False | Whether the tenant has the Meraki Cloud integration enabled. |
| `meraki_api_host` | string | no | default='api.meraki.com' | Meraki dashboard API host. |
| `meraki_org_id` | string | no |  | Meraki organization identifier the tenant is bound to. |
| `meraki_dashboard_api_key` | string | no |  | Meraki dashboard API key. Write-only; never returned in responses. |
| `meraki_integration_created_by` | string | no |  | Email of the user who configured the Meraki integration. |
| `meraki_integration_created_at` | number | no |  | Unix timestamp at which the Meraki integration was configured. |
| `tls_cert_edgeflow_metadata` | [EdgeFlowTLSCertInfoSchema](#schema-edgeflowtlscertinfoschema) \| null | no |  | Metadata for the installed EdgeFlow TLS certificate, if any. |
| `subscription_plan_type` | string \| null | no | one of {'trial', 'starter', 'pro', 'enterprise', 'legacy'} | Onboarding |
| `referral_id` | string \| null | no | default=None | Referral identifier captured at tenant onboarding. |
| `subscription_plan` | object \| null | no |  | Details of the subscription plan in effect for the tenant. |

### `TenantUserSchema` <a id='schema-tenantuserschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `tenant_id` | string | no |  | Identifier of the tenant the user belongs to. |
| `user_id` | string | no |  | Unique user identifier. |
| `email` | string | no |  | User's email address. |
| `machine_user` | boolean \| null | no | default=False | Whether the user is a machine user authenticating via API key. |
| `given_name` | string | no |  | User's given name. |
| `surname` | string | no |  | User's surname. |
| `last_auth` | number | no |  | Unix timestamp of the user's most recent authentication. |
| `last_auths` | list[any] | no |  | Recent authentication timestamps for the user. |
| `role` | string | no | default='tenant_user' | Tenant role assigned to the user. |
| `mfa_active` | list[any] | no |  | Multi-factor authentication (MFA). |

### `CreateTenantUserSchema` <a id='schema-createtenantuserschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `user_id` | string | no | default=None | Identifier of an existing user to add to the tenant. Omit when creating a machine user. |
| `tenant_role` | string | no | default='tenant_user' | Tenant role to assign to the user being added. |
| `machine_user` | boolean \| null | no | default=False | Optional. Indicates whether the tenant user to be added is a machine user or not. |

### `CreateTenantUserResponseSchema` <a id='schema-createtenantuserresponseschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `status` | string | no | default=None | Outcome of the add-user operation. |
| `added_user_id` | string | no | default=None | Identifier of the user that was added. |
| `added_user_email` | string | no | default=None | Email of the user that was added. |
| `added_to_tenant_id` | string | no | default=None | Identifier of the tenant the user was added to. |
| `added_user_role` | string | no | default=None | Tenant role the user was added with. |
| `machine_user` | boolean | no |  | Whether the added user is a machine user. |
| `api_key` | [ApiKeySchema](#schema-apikeyschema) | no |  | API key issued for the newly created machine user. Returned only at creation time. |
| `added_by_user_email` | string | no | default=None | Email of the user who performed the add operation. |

### `UserSchema` <a id='schema-userschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `user_id` | string | no |  | Unique user identifier. |
| `email` | string | no | default=None | User's email address. For machine users, an identifier that does not contain `@`. |
| `password` | string | no | default=None | User password. Write-only; never returned in responses. |
| `given_name` | string | no | default=None | User's given name. |
| `surname` | string | no | default=None | User's surname. |
| `line_user_id` | string | no | default=None | LINE messaging user identifier associated with the user. |
| `machine_user` | boolean \| null | no | default=False | Whether the user is a machine user authenticating via API key. |
| `created_at` | number | no | default=None | Unix timestamp at user creation. |
| `modified_at` | number | no | default=None | Unix timestamp of most recent modification. |
| `last_auth` | number | no |  | Unix timestamp of the user's most recent authentication. |
| `last_auths` | list[any] | no |  | Recent authentication timestamps for the user. |
| `password_modified_at` | number | no | default=None | Unix timestamp at which the password was last changed. |
| `tenant_name` | string | no |  | Display name of the user's tenant. |
| `status` | string | no |  | User account status. |
| `default_region` | string | no | default=None | Default region for the user. |
| `custom_data` | any \| null | no |  | Caller-supplied opaque metadata associated with the user. |
| `title` | string | no |  | User's title. |
| `code` | string | no | default=None | One-time code associated with the user (e.g. for invitation acceptance). |
| `mfa_active` | list[any] | no |  | Multi-factor authentication (MFA). |
| `realm_id` | string | no | default=None | The realm that the user will use to authenticate, if any. |
| `roles` | list[any] \| null | no |  | System roles. system roles only, not tenant roles. |
| `api_key` | [ApiKeySchema](#schema-apikeyschema) | no |  | Used only when provisioning machine users. |
| `first_login` | boolean | no | default=False | True when the user is authenticating for the first time. |
