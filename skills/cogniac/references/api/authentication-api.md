# authentication-api

`authentication-api` is the Cogniac CloudCore service that turns user credentials into a Cogniac JWT and validates JWTs presented by other services. It is the entry point every client must call before making authenticated requests against the rest of the platform: SDKs trade a username/password, API key, or refresh token here for a short-lived bearer JWT scoped to a tenant and role set, and downstream APIs introspect those tokens by calling back into this service.

The service also owns the multi-factor authentication (MFA) lifecycle for time-based one-time passwords (TOTP). End users can enroll an authenticator app, activate TOTP for their account, verify codes, deactivate TOTP, and check whether MFA is enabled. Users who have lost access to their authenticator should contact Cogniac support to recover access.

All endpoints are mounted under the `/21` API version prefix. Authentication on most routes is flexible: callers may present credentials as HTTP Basic, a Cogniac API key (`Authorization: Key <key>`), or a previously issued Bearer JWT, and the service will resolve the active user from whichever scheme is used. The `/21/authorize` endpoint is the only handler that strictly requires a Bearer JWT, since its purpose is to introspect one.

## Endpoints

Grouped by tag. Click any operation to see request/response shapes.

### `API token`

#### `GET /21/token` <a id='op-get-token-21-token-get'></a>
**Issue a Cogniac JWT for the authenticated user**

Authenticate the caller and return a JWT they can use against the rest of the Cogniac API. The caller supplies credentials via the `Authorization` header in one of three forms: HTTP Basic (username and password), `Key <api_key>` (a Cogniac API key issued to the user), or `Bearer <token>` (an existing Cogniac JWT, used to trade up to a tenant-scoped token).

If `tenant_id` is omitted, the response is a "user token" that identifies the user but is not scoped to any tenant. If `tenant_id` is supplied, the caller must be a member of that tenant; the returned token is scoped to that tenant and carries the caller's tenant roles. When the tenant enforces password expiration (`password_expiration_days`), and the caller is authenticating with Basic or Bearer credentials, the call fails if the user's password is past the configured age.

When TOTP MFA is active for the user and credentials are presented as HTTP Basic, an `otp` query parameter must also be supplied; the value is validated against the user's enrolled TOTP secret before a token is issued. Realm (SSO) users cannot use TOTP MFA on this endpoint.

Tenants with an expired contract may have token issuance refused with a renewal-required error; contact Cogniac if your tenant is in this state.

**Auth:** HTTP Basic, API key, or Bearer JWT for the authenticated user

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `tenant_id` | query | string \| null | no | Tenant to scope the issued token to. Omit for a user-scope token. |
| `realm_id` | query | string \| null | no | Identity-provider realm associated with the login session, when authenticating through SSO. |
| `realm_session_id` | query | string \| null | no | Identifier of the SSO realm session that initiated this login. |
| `scope` | query | string \| null | no | Optional scope hint passed through to the issued token. |
| `otp` | query | string \| null | no | Current TOTP code from the user's authenticator app. Required when TOTP MFA is active and the caller is using HTTP Basic credentials. |
| `log_id` | query | string \| null | no | Optional caller-supplied correlation identifier echoed into auth logs. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | `application/json` → any |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 400 | Invalid username or password; machine user attempted Basic auth; tenant not found; caller is not authorized for the requested `tenant_id`. |
| 401 | Bearer token invalid or expired; password verification failed; user was modified after the presented Bearer token was issued. |
| 403 | TOTP MFA is required but `otp` was not provided; user's password has expired for the tenant and must be reset; tenant contract has expired. |
| 412 | TOTP cannot be used for SSO realm users; TOTP is not enabled for the user. |

### `Authorization`

#### `GET /21/authorize` <a id='op-authorize-token-21-authorize-get'></a>
**Introspect a Cogniac JWT**

Validate the Bearer JWT supplied in the `Authorization` header and return its decoded contents: the user's identity, the tenant the token is scoped to, the roles carried by the token, and the issuance time. Downstream services use this endpoint as the trust anchor when they receive a JWT from a client and need to confirm it is well-formed, unexpired, and still consistent with the user's stored record.

If the user's record has been modified since the token was issued (for example, the user was deactivated or their role set changed), the token is rejected and the caller must re-authenticate.

**Auth:** Bearer JWT required

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `log_id` | query | string \| null | no | Optional caller-supplied correlation identifier echoed into auth logs. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | `application/json` → [GetAuthorizeResponse](#schema-getauthorizeresponse) |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 401 | Missing Bearer token in the `Authorization` header; supplied Bearer token is invalid or expired; user was modified since the token was issued. |
| 403 | Bearer token failed authorization checks. |

### `Multifactor Authentication (MFA)`

#### `GET /21/users/mfa/status` <a id='op-get-mfa-status-21-users-mfa-status-get'></a>
**Return MFA status for the calling user**

Report whether TOTP-based multi-factor authentication is currently active for the calling user. The response field `totp` is `"active"` if TOTP is enrolled and enabled, and `"inactive"` otherwise. Use this to drive UI that decides whether to prompt for an OTP at login or to offer the enrollment flow.

**Auth:** HTTP Basic, API key, or Bearer JWT for the authenticated user

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `log_id` | query | string \| null | no | Optional caller-supplied correlation identifier echoed into auth logs. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | `application/json` → [MFAStatusResponse](#schema-mfastatusresponse) |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 401 | Credentials presented in the `Authorization` header are invalid or missing. |

#### `POST /21/users/mfa/totp/activate` <a id='op-activate-mfa-totp-21-users-mfa-totp-activate-post'></a>
**Activate enrolled TOTP for the calling user**

Complete TOTP enrollment by proving the user has successfully configured their authenticator app. The caller must have already called `POST /21/users/mfa/totp/enroll` to receive an `otpauth` URI and load it into an authenticator. This call verifies the supplied `otp` against the enrolled TOTP secret and, on success, marks TOTP as active for the user. Subsequent password-based logins will then require an OTP.

The caller must re-present their password in the request body as a second factor.

**Auth:** HTTP Basic, API key, or Bearer JWT for the authenticated user

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `log_id` | query | string \| null | no | Optional caller-supplied correlation identifier echoed into auth logs. |

**Request body** (`application/json`, required: **yes**): [ActivateTOTPRequest](#schema-activatetotprequest)

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | `application/json` → [ActivateTOTPResponse](#schema-activatetotpresponse) |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 400 | The supplied one-time password is not valid; password verification failed. |
| 401 | Caller could not be authenticated. |
| 412 | TOTP is already enabled for the user, or enrollment has not been started (no TOTP secret on file). |

#### `POST /21/users/mfa/totp/deactivate` <a id='op-deactivate-totp-21-users-mfa-totp-deactivate-post'></a>
**Deactivate TOTP for the calling user**

Disable TOTP multi-factor authentication for the calling user. After this call succeeds, password-only logins resume working for the account. The caller must re-present their password in the request body to confirm the change.

**Auth:** HTTP Basic, API key, or Bearer JWT for the authenticated user

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `log_id` | query | string \| null | no | Optional caller-supplied correlation identifier echoed into auth logs. |

**Request body** (`application/json`, required: **yes**): [DeactivateTOTPRequest](#schema-deactivatetotprequest)

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | `application/json` → [DeactivateTOTPResponse](#schema-deactivatetotpresponse) |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 401 | Caller could not be authenticated. |
| 412 | TOTP is not currently enabled for the user. |

#### `POST /21/users/mfa/totp/enroll` <a id='op-enroll-totp-21-users-mfa-totp-enroll-post'></a>
**Begin TOTP enrollment for the calling user**

Start the process of enabling TOTP MFA for the calling user. On success, the response carries an `otpauth://` URI that the user loads into an authenticator app (typically by scanning a QR code rendered from the URI). The user then completes enrollment by calling `POST /21/users/mfa/totp/activate` with a current OTP from the authenticator.

The caller must re-present their password in the request body as a second factor. Enrollment fails if TOTP is already active for the user, to avoid replacing an existing authenticator secret with a new one that the user has not yet configured. SSO realm users cannot enroll in TOTP through this endpoint.

**Auth:** HTTP Basic, API key, or Bearer JWT for the authenticated user

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `log_id` | query | string \| null | no | Optional caller-supplied correlation identifier echoed into auth logs. |

**Request body** (`application/json`, required: **yes**): [EnrollTOTPRequest](#schema-enrolltotprequest)

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | `application/json` → [EnrollTOTPResponse](#schema-enrolltotpresponse) |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 401 | Password verification failed. |
| 412 | TOTP cannot be enabled for SSO realm users; TOTP is already enabled for the user. |
| 500 | Failed to persist the generated TOTP secret. |

#### `POST /21/users/mfa/totp/verify` <a id='op-verify-totp-21-users-mfa-totp-verify-post'></a>
**Verify a TOTP code for the calling user**

Check that the supplied `otp` is a currently valid TOTP code for the calling user's enrolled authenticator. Use this to confirm an OTP outside of the login flow — for example, to gate access to a sensitive UI action. The endpoint does not issue a token; it only reports whether the code matched.

TOTP must already be enabled for the user; SSO realm users cannot use TOTP and will be refused.

**Auth:** HTTP Basic, API key, or Bearer JWT for the authenticated user

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `log_id` | query | string \| null | no | Optional caller-supplied correlation identifier echoed into auth logs. |

**Request body** (`application/json`, required: **yes**): [VerifyTOTPRequest](#schema-verifytotprequest)

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | `application/json` → [VerifyTOTPResponse](#schema-verifytotpresponse) |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 400 | The supplied one-time password is not valid. |
| 412 | TOTP cannot be used for SSO realm users; TOTP is not enabled for the user. |

---

## Schema Components

All Pydantic-derived schemas referenced above. Constraints (enum, range, length, pattern, default) are inline so an API consumer can write a correct client without reading Pydantic source.

### `ActivateTOTPRequest` <a id='schema-activatetotprequest'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `otp` | string | **yes** |  | Current TOTP code from the user's authenticator app. |
| `password` | string | **yes** |  | The calling user's password, re-presented to confirm activation. |

### `ActivateTOTPResponse` <a id='schema-activatetotpresponse'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `success` | boolean | **yes** |  | `true` when TOTP was activated for the user. |

### `DeactivateTOTPRequest` <a id='schema-deactivatetotprequest'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `password` | string | **yes** |  | The calling user's password, re-presented to confirm deactivation. |

### `DeactivateTOTPResponse` <a id='schema-deactivatetotpresponse'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `success` | boolean | **yes** |  | `true` when TOTP was deactivated for the user. |

### `EnrollTOTPRequest` <a id='schema-enrolltotprequest'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `password` | string | **yes** |  | The calling user's password, re-presented to authorize enrollment. |

### `EnrollTOTPResponse` <a id='schema-enrolltotpresponse'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `uri` | string | **yes** |  | `otpauth://` URI to load into an authenticator app to provision the user's TOTP secret. |

### `GetAuthorizeResponse` <a id='schema-getauthorizeresponse'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `issued_at` | string | **yes** |  | Time the token was issued. |
| `realm_id` | string \| null | no |  | Identity-provider realm the user authenticated through, when applicable. |
| `realm_session_id` | string \| null | no |  | Identifier of the SSO realm session the token was issued in. |
| `roles` | list[string] | **yes** |  | Roles carried by the token (tenant role plus any system roles). |
| `tenant_id` | string \| null | no |  | Tenant the token is scoped to, or `null` for a user-scope token. |
| `user_email` | string | **yes** |  | Email address of the authenticated user. |
| `user_id` | string | **yes** |  | Identifier of the authenticated user. |

### `HTTPValidationError` <a id='schema-httpvalidationerror'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `detail` | list[[ValidationError](#schema-validationerror)] | no |  | Per-field validation failures. |

### `MFAStatusResponse` <a id='schema-mfastatusresponse'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `totp` | string | **yes** |  | `"active"` if TOTP is enabled for the user, `"inactive"` otherwise. |

### `ValidationError` <a id='schema-validationerror'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `ctx` | object | no |  | Additional context for the validation failure. |
| `input` | any | no |  | The input value that failed validation. |
| `loc` | list[string \| integer] | **yes** |  | Location of the failure within the request (path of field names/indexes). |
| `msg` | string | **yes** |  | Human-readable validation error message. |
| `type` | string | **yes** |  | Validation error type identifier. |

### `VerifyTOTPRequest` <a id='schema-verifytotprequest'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `otp` | string | **yes** |  | TOTP code from the user's authenticator app to verify. |

### `VerifyTOTPResponse` <a id='schema-verifytotpresponse'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `success` | boolean | **yes** |  | `true` when the supplied OTP matched the user's enrolled TOTP secret. |
