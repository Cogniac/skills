# license-core-api

Create, read, update, and delete Meraki camera licenses for Cogniac tenants, and manage the per-tenant expiration policy that governs how those licenses are activated, renewed, and enforced.

Cogniac uses a license to cap the number of Meraki cameras a tenant may provision into a capture application. Each license carries a device count, an activation date, and a term; the service co-terminates a tenant's licenses against a single tenant-wide expiration date and tracks compliance so that downstream services can block new provisioning once a tenant exceeds its entitlements. Operators (typically license administrators) call this API to issue new licenses, revise existing ones, and tune the notification and grace-period behavior used when a tenant approaches expiration.

All endpoints are served under the `/22` API version prefix. A caller's JWT always identifies a single tenant, and the `tenant_id` path segment must match that token's tenant; cross-tenant access is rejected with `404`. Mutating endpoints additionally require an internal Cogniac role (`cogniac_admin` or `license_admin`); read endpoints accept any authenticated user on the tenant.

## Endpoints

Grouped by tag.

### `License Management`

#### `GET /22/license/{tenant_id}/{license_type}` <a id='op-/22/license/{tenant-id}/{license-type}get'></a>

Return license records and aggregate license information for a tenant, scoped to a single license type. Results are ordered by last update time, most-recently-updated first; pass `reverse=true` to invert that order. The optional `expiration_status`, `start_date`, and `end_date` query parameters narrow the result to licenses whose expiration falls in a given status or window.

The response includes both the per-license records and a roll-up (`license_info`) that carries the tenant's co-termination date, the camera count Meraki currently reports for the tenant, and a `license_compliant` flag used by other services to decide whether new cameras may be added.

**Auth:** Bearer JWT required

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `expiration_status` | query | Literal['expired', 'active', 'all'] | no | Filter by expiration status |
| `start_date` | query | string | no | RFC822 format date specifying start of expiration range to query |
| `end_date` | query | string | no | RFC822 format date specifying start of expiration range to query |
| `reverse` | query | boolean | no | Set true to reverse the default ordering of licenses.  The default false setting, orders the  licenses by last update time, from most to least recently updated. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successfully retrieved the licenses information | `application/json` → [LicensesInfo](#schema-licensesinfo) |
| 404 | Invalid request: - Tenant not found | `application/json` → [Error](#schema-error) |
| 500 | Unexpected error | `application/json` → [Error](#schema-error) |

**Errors:**

| Status | Condition |
|---|---|
| 400 | `start_date` / `end_date` are not valid RFC822 dates, or `start_date` is after `end_date`. |
| 404 | The `tenant_id` does not match the caller's token, or no license information exists for the tenant and license type. |

#### `POST /22/license/{tenant_id}/{license_type}` <a id='op-/22/license/{tenant-id}/{license-type}post'></a>

Create a new license of the specified type for the tenant. The body must conform to [MerakiLicenseCreateRequest](#schema-merakilicensecreaterequest); `device_limit` and `term` (in seconds) are required, and `name` must be non-empty.

If `start_date` is omitted, the server activates the license at `now + start_date_offset` from the tenant's expiration policy. Newly created licenses are co-terminated against the tenant's existing licenses of the same type.

**Auth:** Bearer JWT; required roles: `{cogniac_admin, license_admin}`

**Request body** (`application/json`, required: **yes**): [MerakiLicenseCreateRequest](#schema-merakilicensecreaterequest)

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successfully created a new license for the specified tenant | `application/json` → [License](#schema-license) |
| 400 | Invalid request: - Invalid license type - Unsupported format - License does not conform to schema | `application/json` → [Error](#schema-error) |
| 403 | User does not have authorization to perform this action. User must have license admin role | `application/json` → [Error](#schema-error) |
| 404 | - Tenant not found | `application/json` → [Error](#schema-error) |
| 500 | Unexpected error | `application/json` → [Error](#schema-error) |

**Errors:**

| Status | Condition |
|---|---|
| 404 | The `tenant_id` does not match the caller's token. |
| 500 | License creation failed for an unexpected reason. |

#### `GET /22/license/{tenant_id}/{license_type}/expiration_policy` <a id='op-/22/license/{tenant-id}/{license-type}/expiration-policyget'></a>

Return the expiration policy that governs activation timing, expiry notifications, and the post-expiration grace period for the given tenant and license type.

**Auth:** Bearer JWT required

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successfully retrieves the expiration policy | `application/json` → [ExpirationPolicy](#schema-expirationpolicy) |
| 400 | Invalid request:  - Unknown tenantId  - Unknown licenseType | `application/json` → [Error](#schema-error) |
| 404 | Expiration policy not found | `application/json` → [Error](#schema-error) |
| 500 | Unexpected error | `application/json` → [Error](#schema-error) |

**Errors:**

| Status | Condition |
|---|---|
| 404 | The `tenant_id` does not match the caller's token, or no expiration policy exists for the tenant and license type. |

#### `PATCH /22/license/{tenant_id}/{license_type}/expiration_policy` <a id='op-/22/license/{tenant-id}/{license-type}/expiration-policypatch'></a>

Update the expiration policy for the tenant and license type. Only fields present in the request body are modified; omitted fields retain their previous values.

**Auth:** Bearer JWT; required roles: `{cogniac_admin, license_admin}`

**Request body** (`application/json`, required: **yes**): [ExpirationPolicy](#schema-expirationpolicy)

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successfully created the expiration policy | `application/json` → [ExpirationPolicy](#schema-expirationpolicy) |
| 400 | Invalid request  - Unknown tenantId  - Unknown licenseType  - Unsupported format  - ExpirationPolicy does not conform to schema | `application/json` → [Error](#schema-error) |
| 403 | User does not have authorization to perform this action. User must have license admin role | `application/json` → [Error](#schema-error) |
| 404 | Expiration policy not found | `application/json` → [Error](#schema-error) |
| 500 | Unexpected error | `application/json` → [Error](#schema-error) |

**Errors:**

| Status | Condition |
|---|---|
| 404 | The `tenant_id` does not match the caller's token, or no expiration policy exists for the tenant and license type. |

#### `POST /22/license/{tenant_id}/{license_type}/compliance_status` <a id='op-/22/license/{tenant-id}/{license-type}/compliance-statuspost'></a>

Trigger a recompute of the tenant's license-compliance state for the given license type. The service reconciles the tenant's licensed device count against the cameras Meraki currently reports and updates the `license_compliant` flag returned from the license-info endpoint accordingly. The call returns as soon as the recompute has been accepted; the updated status is observable on subsequent reads of `GET /22/license/{tenant_id}/{license_type}`.

**Auth:** Bearer JWT; required roles: `{cogniac_admin, license_admin}`

**Path params:**

| Name | Type | Description |
|---|---|---|
| `tenant_id` | string | Identifier of the tenant whose compliance status should be recomputed. |
| `license_type` | string (enum) | License type identifier. Must be a supported [licenseType](#schema-licensetype) value. |

**Responses:**

| Status | Description |
|---|---|
| 204 | Compliance recompute accepted. |

**Errors:**

| Status | Condition |
|---|---|
| 404 | The `tenant_id` does not match the caller's token. |

#### `DELETE /22/license/{tenant_id}/{license_type}/id/{license_id}` <a id='op-/22/license/{tenant-id}/{license-type}/id/{license-id}delete'></a>

Delete a single license by id. The tenant's co-termination date and `license_compliant` flag are recomputed from the remaining licenses; cameras that were entitled by the deleted license may cause the tenant to fall out of compliance.

**Auth:** Bearer JWT; required roles: `{cogniac_admin, license_admin}`

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successfully deleted the license | (no body) |
| 400 | Invalid Request:   - Invalid License type | `application/json` → [Error](#schema-error) |
| 403 | User does not have authorization to perform this action. User must have license admin role | `application/json` → [Error](#schema-error) |
| 500 | Unexpected error | `application/json` → [Error](#schema-error) |

**Errors:**

| Status | Condition |
|---|---|
| 404 | The `tenant_id` does not match the caller's token. |
| 500 | License deletion failed for an unexpected reason. |

#### `GET /22/license/{tenant_id}/{license_type}/id/{license_id}` <a id='op-/22/license/{tenant-id}/{license-type}/id/{license-id}get'></a>

Retrieve a single license by id.

**Auth:** Bearer JWT required

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successfully retrieves the license | `application/json` → [License](#schema-license) |
| 400 | Invalid Request - Invalid license type | `application/json` → [Error](#schema-error) |
| 404 | - Tenant not found - License not found | `application/json` → [Error](#schema-error) |
| 500 | Unexpected error | `application/json` → [Error](#schema-error) |

**Errors:**

| Status | Condition |
|---|---|
| 404 | The `tenant_id` does not match the caller's token, or no license exists with the given `license_id` for that tenant and license type. |

#### `PATCH /22/license/{tenant_id}/{license_type}/id/{license_id}` <a id='op-/22/license/{tenant-id}/{license-type}/id/{license-id}patch'></a>

Update a single license. Only fields present in the request body are modified. Server-managed fields (`time_created`, `time_updated`) cannot be set by the caller; `start_date`, when supplied, must conform to the tenant's expiration policy.

**Auth:** Bearer JWT; required roles: `{cogniac_admin, license_admin}`

**Request body** (`application/json`, required: **yes**): [MerakiLicenseUpdateRequest](#schema-merakilicenseupdaterequest)

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successfully updated the license | `application/json` → [License](#schema-license) |
| 400 | Invalid Request: - Invalid License type - License does not conform to schema | `application/json` → [Error](#schema-error) |
| 403 | User does not have authorization to perform this action. User must have license admin role | `application/json` → [Error](#schema-error) |
| 404 | - Tenant not found - License not found | `application/json` → [Error](#schema-error) |
| 500 | Unexpected error | `application/json` → [Error](#schema-error) |

**Errors:**

| Status | Condition |
|---|---|
| 400 | The request body is malformed or fails Pydantic validation. |
| 404 | The `tenant_id` does not match the caller's token, or no license exists with the given `license_id`. |
| 500 | License update failed for an unexpected reason. |

---

## Schema Components

All Pydantic-derived schemas referenced above. Constraints (enum, range, length, pattern, default) are inline so an API consumer can write a correct client without reading Pydantic source.

### `Error` <a id='schema-error'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `message` | string | **yes** |  | A human readable error message |

### `ExpirationPolicy` <a id='schema-expirationpolicy'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `emails` | list[string] | no |  | Email address to send expiry notifications |
| `grace_period` | integer | no |  | Days post co-termination/expiration at which enforcement is initiated Defaults to 30 days |
| `notification_url` | list[string] | no |  | URLs to which expiry notification is posted |
| `notify_days_before_expiry` | integer | no |  | Days prior to expiration at which notification is sent Defaults to 60 days |
| `notify_days_expiry_cadence` | integer | no |  | Interval in days at which expiry notification is sent Defaults to 5 days |
| `start_date_offset` | integer | no |  | Days to activate license after creation Defaults to 30 days |

### `License` <a id='schema-license'></a>

License Object

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `license` | [MerakiLicense](#schema-merakilicense) | no |  | The stored Meraki license record. |

### `LicensesInfo` <a id='schema-licensesinfo'></a>

Licenses information - includes meta data for a type of license as well as the list of licenses

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `license_info` | [MerakiCameraLicenseInfo](#schema-merakicameralicenseinfo) | no |  | Aggregate license information for the tenant and license type. |
| `license_type` | [licenseType](#schema-licensetype) | no |  | License type these records describe. |

### `MerakiCameraLicenseInfo` <a id='schema-merakicameralicenseinfo'></a>

Response for GET License Information

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `co_termination_date` | string | no |  | RFC822 formatted co-termination date of licenses |
| `discovered_camera_count` | string | no |  | Number of discovered cameras; Acquired from Meraki APIs |
| `license_compliant` | boolean | no |  | License compliant flag; Used for enforcement. When false:   - Prevents provisioning of new cameras   - Prevents adding/updating a camera in the capture application |
| `licenses` | list[[MerakiLicense](#schema-merakilicense)] | no |  | List of licenses |

### `MerakiLicense` <a id='schema-merakilicense'></a>

Meraki license

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `compliance_type` | Literal['co-termination'] | **yes** |  | Meraki license type |
| `device_limit` | integer | **yes** |  | Maximum number of devices supported |
| `license_id` | [licenseId](#schema-licenseid) | no |  | Server-assigned identifier for this license. |
| `name` | string | **yes** |  | Licence name |
| `order_id` | string | no |  | order id associated with this license |
| `start_date` | integer | no |  | Epoch timestamp when license was activated; When zero or not set, the server will set based on the expiration policy start date offset. |
| `term` | integer | **yes** |  | License term in seconds |
| `time_created` | integer | no |  | Epoch timestamp when the license record was created; Set by the server |
| `time_updated` | integer | no |  | Epoch timestamp when the license record was updated; Set by the server |

### `MerakiLicenseCreateRequest` <a id='schema-merakilicensecreaterequest'></a>

Meraki license

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `compliance_type` | Literal['co-termination'] | **yes** |  | Meraki license type |
| `device_limit` | integer | **yes** | minimum=1 | Maximum number of devices supported |
| `name` | string | **yes** | minLength=1 | Licence name |
| `order_id` | string | no |  | order id associated with this license |
| `start_date` | number | no |  | Epoch timestamp when license was activated; When not set by the user, the server will set based on the expiration policy start date offset. |
| `term` | integer | **yes** | minimum=86400; maximum=157700000 | License term in seconds |

### `MerakiLicenseUpdateRequest` <a id='schema-merakilicenseupdaterequest'></a>

Meraki license

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `compliance_type` | Literal['co-termination'] | **yes** |  | Meraki license type |
| `device_limit` | integer | **yes** |  | Maximum number of devices supported |
| `license_id` | [licenseId](#schema-licenseid) | no |  | Identifier of the license being updated. Must match the `license_id` in the path. |
| `name` | string | **yes** |  | Licence name |
| `order_id` | string | no |  | order id associated with this license |
| `start_date` | integer | no |  | Epoch timestamp when license was activated; When zero or not set, the server will set based on the expiration policy start date offset. |
| `term` | integer | **yes** |  | License term in seconds |

### `licenseId` <a id='schema-licenseid'></a>

The unique identifier of a license

_(no properties; raw type = `string`)_

### `licenseType` <a id='schema-licensetype'></a>

License type identifier

**Enum:** 'meraki-camera'

### `tenantId` <a id='schema-tenantid'></a>

The unique identifier of a tenant

_(no properties; raw type = `string`)_
