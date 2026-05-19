# token-core-api

Issues JWT bearer tokens used to authenticate every other call to the
Cogniac API. Clients exchange one of three credential types — username
and password (HTTP Basic), an API key, or an existing unexpired JWT —
for an `access_token` that is presented as `Authorization: Bearer
<token>` on subsequent requests.

A typical integration flow is:

1. List the tenants the user can access (see
   `GET /1/users/{user_id}/tenants` on the user service).
2. Call `GET /1/token` with `tenant_id` set to the target tenant to
   obtain a tenant-scoped bearer token.
3. Send that token on every subsequent API request until it expires,
   then re-authenticate.

Tokens are scoped per tenant: to switch tenants, request a new token
with a different `tenant_id`. Tokens minted without a `tenant_id` are
valid only for endpoints that do not require a tenant context.

## Endpoints

### `GET /1/token`

**Authenticate a user and provide a JWT token for accessing a specific tenant on behalf of the user**

Exchange credentials for a JWT bearer token. The credential type is
selected by the `Authorization` request header:

- `Authorization: Basic <base64(email:password)>` — authenticate with
  a username and password.
- `Authorization: Key <key_id>:<key_secret>` — authenticate with a
  Cogniac API key. Recommended for service accounts and unattended
  integrations.
- `Authorization: Bearer <jwt>` — refresh an existing unexpired token.
  A refresh is rejected if the user record has been modified since the
  presented token was issued; the client must re-authenticate with a
  password or API key.

Pass `tenant_id` to receive a tenant-scoped token suitable for calls
that operate on tenant-owned resources (applications, subjects, media,
etc.). Omit it to receive a token usable only for tenant-agnostic
endpoints such as listing the tenants the caller belongs to.

When the caller's tenant enforces multi-factor authentication via TOTP
and the credential is a username and password, the one-time passcode
must be supplied in the `otp` query parameter. MFA is not evaluated
for API-key or bearer-refresh flows.

The response body is `{"access_token": "<jwt>", "token_type":
"Bearer"}`. Lifetime depends on scope: tenant-scoped tokens are
short-lived and intended for active sessions, while non-tenant-scoped
tokens have a longer lifetime suitable for the initial
tenant-selection step. Clients should treat the token as opaque.

**Auth:** HTTP Basic, API key, or Bearer JWT for the authenticated user

**Query parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `tenant_id` | string | no | Tenant to scope the returned token to. Required for any call that targets tenant-owned resources. |
| `realm_id` | string | no | Realm identifier for SSO/realm-federated logins. |
| `realm_session_id` | string | no | Realm session identifier paired with `realm_id`. |
| `otp` | string | no | One-time passcode for TOTP multi-factor authentication. Required when the user has TOTP enabled and the credential is a username and password. |

**Errors:**

- `401` — missing or malformed `Authorization` header; invalid
  username, password, or API key; expired or otherwise invalid JWT;
  user record has been modified since the presented token was issued;
  too many recent failed login attempts for the user.
- `403` — multi-factor authentication is required but `otp` was not
  supplied or did not verify; the user's password has expired and
  must be changed; the tenant's contract has expired.
- `400` — caller is not a member of the requested `tenant_id`, or the
  tenant does not exist.

### `GET /1/oauth/token`

**Trade a user/password for OAuth tokens**

Legacy multi-tenant authentication endpoint. Accepts HTTP Basic
credentials only and returns a richer response body that includes user
and tenant identifiers alongside the access token.

Two modes are supported:

- Supply `tenant_id` to receive a single tenant-scoped token for that
  tenant. The response is a single `LoginResponseSchema` object.
- Supply `scope=all` (and no `tenant_id`) to receive one token per
  tenant the user belongs to. The response is an array of
  `LoginResponseSchema` objects.

Exactly one of `tenant_id` or `scope=all` must be provided. New
integrations should prefer `GET /1/token`, which supports API keys and
bearer-token refresh in addition to HTTP Basic.

**Auth:** no auth required (caller must present HTTP Basic credentials in the `Authorization` header)

**Query parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `tenant_id` | string | no | Tenant to scope the returned token to. Mutually exclusive with `scope=all`. |
| `scope` | string | no | Set to `all` to receive a token for every tenant the user belongs to. Mutually exclusive with `tenant_id`. |

**Errors:**

- `422` — missing or malformed Basic credentials, invalid username or
  password, neither `tenant_id` nor `scope=all` supplied, or the
  supplied `tenant_id` was not found.
- `400` — caller is not a member of the supplied `tenant_id`.

## Schemas

### `LoginRequestSchema` <a id='schema-loginrequestschema'></a>

Request envelope for the token-exchange endpoints. The `auth` value is
the contents of the `Authorization` request header
(`Basic <base64(email:password)>`, `Key <key_id>:<key_secret>`, or
`Bearer <jwt>`); the remaining fields are supplied as query
parameters.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `auth` | string | **yes** |  | Contents of the `Authorization` header. Carries the credential used to authenticate the request. |
| `tenant_id` | string | no |  | Tenant to scope the returned token to. |
| `realm_id` | string | no |  | Realm identifier for SSO/realm-federated logins. |
| `realm_session_id` | string | no |  | Realm session identifier paired with `realm_id`. |
| `scope` | string | no |  | Set to `all` on `/1/oauth/token` to receive a token for every tenant the user belongs to. |
| `otp` | string | no |  | One-time passcode for TOTP multi-factor authentication. |

### `LoginResponseSchema` <a id='schema-loginresponseschema'></a>

Response body returned by `GET /1/oauth/token`. When `scope=all` is
used, the endpoint returns an array of these objects, one per tenant
the user belongs to.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `user_id` | string | no |  | Identifier of the authenticated user. |
| `user_email` | string | no |  | Email address of the authenticated user. |
| `tenant_id` | string | no |  | Tenant the returned `access_token` is scoped to. |
| `tenant_name` | string | no |  | Human-readable name of `tenant_id`. |
| `access_token` | string | no |  | JWT bearer token. Present as `Authorization: Bearer <access_token>` on subsequent requests. |
| `token_type` | string | no |  | Token type for the `Authorization` header. Always `Bearer`. |
| `expires_in` | integer | no |  | Lifetime of `access_token` in seconds from issue. |
| `super_user` | integer | no |  | Non-zero if the authenticated user holds elevated Cogniac-staff privileges. |
| `organization` | string | no |  | Organization the tenant belongs to, when applicable. |
