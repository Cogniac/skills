# network-camera-core-api

Register and manage network cameras (RTSP, MJPEG, GigE Vision/GenICam) that supply media to Cogniac applications. Each network camera represents an IP camera or other streaming source bound to a tenant. Cameras may carry geographic location, pose, lens, and sensor calibration data, and supply media to a `camera_capture` application that ingests their frames into the Cogniac platform.

All endpoints require Bearer-token authentication and operate within the caller's tenant.

## Endpoints

### `POST /1/networkCameras`

**Creates a network camera**

Register a new network camera in the caller's tenant. The request body must include `url` and `camera_name`; other fields from [NetworkCameraSchema](#schema-networkcameraschema) are optional.

On success, the server allocates a `network_camera_id`, provisions a private subject to carry frames captured from this camera (its identifier is returned as `subject_uid`), and returns the full camera record.

**Auth:** Bearer JWT required

**Request body:** [NetworkCameraSchema](#schema-networkcameraschema)

**Response:** `200` — the created [NetworkCameraSchema](#schema-networkcameraschema).

### `POST /1/networkCameras/{id}`

**Updates a network camera**

Update mutable fields on the network camera identified by `id`. Only fields present in the request body are modified; the response is the updated camera record.

Updating any of the camera pose, intrinsic, or distortion fields (e.g. `pitch`, `yaw`, `roll`, `tx_m`/`ty_m`/`tz_m`, `resolution_h_px`/`resolution_v_px`, `focal_length_*`, `pixel_*`, `ch_px`/`cv_px`, `radial_distortion_coefficients`, `tangential_distortion_coefficients`, `origin_*`, `*_axis_*`) marks the camera model as changed; the timestamp of the change is recorded on the camera record.

If the camera is attached to a `camera_capture` application, the caller must be a manager of that application.

**Auth:** Bearer JWT required (when the camera is attached to a `camera_capture` or `network_camera` application, the caller must be listed as an app manager on that application or hold the `ef_device` or `tenant_admin` role)

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Network camera identifier. |

**Request body:** partial [NetworkCameraSchema](#schema-networkcameraschema)

**Response:** `200` — the updated [NetworkCameraSchema](#schema-networkcameraschema).

**Errors:**
- `404` — camera not found in the caller's tenant.
- `403` — caller is not a manager of the camera's associated application.

### `DELETE /1/networkCameras/{id}`

**Deletes a network camera**

Permanently delete the network camera identified by `id`. The camera must not be associated with an active application; remove it from any `camera_capture` application before deletion.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Network camera identifier. |

**Response:** `204 No Content`.

**Errors:**
- `404` — camera not found in the caller's tenant.
- `412` — camera is in use by an application and cannot be deleted.

### `GET /1/networkCameras/{id}`

**Retrieves network camera**

Return the network camera identified by `id`, including any extracted GenICam feature attributes (`genicam_features`) previously uploaded for the camera.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Network camera identifier. |

**Response:** `200` — [NetworkCameraSchema](#schema-networkcameraschema).

**Errors:**
- `404` — camera not found in the caller's tenant.

### `POST /1/networkCameras/{camera_id}/genicam`

**Updates a network camera's description GenICam XML**

Upload the GenICam description XML for a GigE Vision / GenICam-compliant camera. The request body must be a `multipart/form-data` upload containing the XML file. The server validates the XML, stores it as the camera's GenICam description, and extracts a summary of feature attributes that subsequent `GET /1/networkCameras/{id}` calls return in `genicam_features`.

This endpoint is restricted to EdgeFlow appliances enrolling discovered cameras and to Cogniac support staff.

**Auth:** Bearer JWT; required roles: `{cogniac_support, ef_device}`

**Path params:**

| Name | Type | Description |
|---|---|---|
| `camera_id` | string | Network camera identifier. |

**Request body:** `multipart/form-data` with a single XML file part.

**Response:** `200` — `text/xml` body containing the stored GenICam XML.

**Errors:**
- `400` — request did not include a file, the file was empty, or the XML failed validation.
- `404` — camera not found in the caller's tenant.

### `GET /1/networkCameras/{camera_id}/genicam`

**Retrieves a network camera's description GenICam XML**

Return the GenICam description XML previously uploaded for the camera. Supports HTTP `Range` requests for partial fetches of the XML body.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `camera_id` | string | Network camera identifier. |

**Response:** `200` — `text/xml` body containing the camera's GenICam description.

**Errors:**
- `404` — camera not found, or no GenICam XML has been uploaded for this camera.

## Schemas

### `NetworkCameraSchema` <a id='schema-networkcameraschema'></a>

A registered network camera. Carries identification, stream connection, geographic location, sensor/lens intrinsics, distortion model, and pose used to interpret media produced by the camera.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `network_camera_id` | string | no |  | Server-assigned unique identifier for the camera. |
| `tenant_id` | string | no |  | Tenant that owns the camera. |
| `subject_uid` | string | no |  | Identifier of the subject that receives media captured from this camera. |
| `alt_subject_uid` | list[string] | no |  | Additional subjects the camera's media is associated with. |
| `created_by` | string | no |  | Email of the user that registered the camera. |
| `url` | string \| null | **yes** | default=None | Stream URL for the camera (for example, `rtsp://user:pass@host:port/path` or an MJPEG HTTP URL). |
| `camera_name` | string \| null | **yes** | default=None | Human-readable camera name; included as a tag on media captured from this camera. |
| `description` | string \| null | no | default=None | Free-form description of the camera. |
| `active` | boolean \| null | no |  | When `true`, frames from this camera are processed; when `false`, capture is paused. |
| `created_at` | number | no |  | Unix timestamp when the camera was registered. |
| `modified_at` | number | no |  | Unix timestamp of the most recent update. |
| `lat` | number \| null | no | default=None | Camera latitude in decimal degrees. |
| `lon` | number \| null | no | default=None | Camera longitude in decimal degrees. |
| `hae` | number \| null | no | default=None | Height above ellipsoid in meters; reserved for aerial/UAV cameras. |
| `discovered_by` | string \| null | no | default=None | Identifier of the EdgeFlow appliance that discovered the camera, if any. |
| `gateway_id` | string \| null | no | default=None | Deprecated. Use `discovered_by` instead. |
| `genicam_xml` | string | no |  | Reserved; the GenICam description XML is uploaded and retrieved via the `/1/networkCameras/{camera_id}/genicam` endpoints. |
| `genicam_features` | any | no |  | Summary of GenICam feature attributes extracted from the uploaded description XML. |
| `last_pose_change_timestamp` | number | no |  | camera pose and model related parameters approximate time of last camera pose change.  Images before this time were not generated by the current camera pose and the current pose is invalid for computations of images before this timestamp, updated by user |
| `last_model_change_timestamp` | number | no |  | approximate time of last camera model change, updated by user |
| `orientation` | integer \| null | no | default=0 | gige cam rotation - 0, 90, 180, 270 degrees. |
| `resolution_h_px` | integer \| null | no | default=None | camera intrinsic parameters resolution in horizontal/vertical dimension |
| `resolution_v_px` | integer \| null | no | default=None | Vertical resolution in pixels. |
| `pixel_h_um` | number \| null | no | default=None | pixel (unit cell) horizontal/vertical in micrometers |
| `pixel_v_um` | number \| null | no | default=None | Vertical pixel pitch in micrometers. |
| `focal_length_h_mm` | number \| null | no | default=None | focal length in mm |
| `focal_length_v_mm` | number \| null | no | default=None | Vertical focal length in millimeters. |
| `skew` | number | no | default=0 | skew reflects pixel deviation from a square. Equals zero for good cameras |
| `ch_px` | number \| null | no | default=None | Principal point in terms of pixel dimensions in horizontal/vertical direction. Expected to be at a sensor's center, but precise calibration can provide different estimates |
| `cv_px` | number \| null | no | default=None | Vertical pixel coordinate of the principal point. |
| `radial_distortion_coefficients` | list[number] | no |  | radially symmetric distortions arising from the symmetry of a photographic lens |
| `tangential_distortion_coefficients` | list[number] | no |  | tangential distortion caused by physical elements in a lens not being perfectly aligned |
| `pitch` | number \| null | no | default=None | camera pose, yaw, pitch, roll in radians |
| `yaw` | number \| null | no | default=None | Yaw component of the camera pose, in radians. |
| `roll` | number \| null | no | default=None | Roll component of the camera pose, in radians. |
| `tx_m` | number \| null | no | default=None | translation vector in meters.  (camera location in meters) |
| `ty_m` | number \| null | no | default=None | Y component of the camera translation vector in meters. |
| `tz_m` | number \| null | no | default=None | Z component of the camera translation vector in meters. |
| `origin_x` | number \| null | no | default=None | pixel coordinate of the origin, and x, y, z axes |
| `origin_y` | number \| null | no | default=None | Pixel y-coordinate of the world-frame origin projected into the image. |
| `x_axis_x` | number \| null | no | default=None | Pixel x-coordinate of the world x-axis endpoint projected into the image. |
| `x_axis_y` | number \| null | no | default=None | Pixel y-coordinate of the world x-axis endpoint projected into the image. |
| `y_axis_x` | number \| null | no | default=None | Pixel x-coordinate of the world y-axis endpoint projected into the image. |
| `y_axis_y` | number \| null | no | default=None | Pixel y-coordinate of the world y-axis endpoint projected into the image. |
| `z_axis_x` | number \| null | no | default=None | Pixel x-coordinate of the world z-axis endpoint projected into the image. |
| `z_axis_y` | number \| null | no | default=None | Pixel y-coordinate of the world z-axis endpoint projected into the image. |
| `spec_version_major` | string \| null | no | default=None | camera info reported during camera discovery (e.g., by GigE protocol) |
| `spec_version_minor` | string \| null | no | default=None | GigE Vision specification minor version reported by the camera. |
| `device_mode` | string \| null | no | default=None | Device mode reported by the camera during discovery. |
| `IP_config_options` | string \| null | no | default=None | IP configuration options supported by the camera. |
| `IP_config_current` | string \| null | no | default=None | Active IP configuration mode on the camera. |
| `current_IP` | string \| null | no | default=None | Camera's current IP address. |
| `current_subnet_mask` | string \| null | no | default=None | Camera's current subnet mask. |
| `default_gateway` | string \| null | no | default=None | Camera's configured default gateway. |
| `mac_address` | string \| null | no | default=None | Camera's MAC address. |
| `model_name` | string \| null | no | default=None | Model name reported by the camera. |
| `serial_number` | string \| null | no | default=None | Serial number reported by the camera. |
| `device_version` | string \| null | no | default=None | Firmware/device version reported by the camera. |
| `manufacturer_name` | string \| null | no | default=None | Manufacturer name reported by the camera. |
| `manufacturer_info` | string \| null | no | default=None | Additional manufacturer-supplied information. |
| `user_defined_name` | string \| null | no | default=None | User-defined name programmed onto the camera device. |
| `gige_features` | list[object] \| null | no |  | List of GigE Vision feature descriptors reported by the camera. |
| `custom_configuration` | any | no |  | Additional camera configuration. |

