# user-core-api

User account management for the Cogniac platform: accepting invitations to create accounts, updating profile fields, issuing and revoking API keys, requesting password resets, listing the tenants a user belongs to, and managing the user's pending tenant invitations.

A Cogniac user is a global identity (one email = one user) that can be a member of one or more tenants. The typical lifecycle is:

1. A tenant admin invites a user by email (handled by the tenants API, not here).
2. The invitee calls `POST /1/users` with the invite code to create their account.
3. The user authenticates and obtains a bearer token (via the token endpoint, not here).
4. The user manages their profile, API keys, and pending invitations through the endpoints below.

Unless noted otherwise, all timestamps are Unix epoch seconds. The literal string `current` is accepted in place of a user id in path parameters and is resolved server-side to the authenticated user.

## Endpoints

### `POST /1/users`

**Accept an invitation to create a Cogniac account**

Create a new user in system; authenticated only by code in invite table.

If user presents the correct invite code an account will be created
for the specified email address and the user will be added to the tenant
specified in the invitation record.

The invitation must still be in `pending` status and the `email` in the request must match the address that was invited. If the invitation is bound to a third-party identity provider (realm), the response carries a `redirect_uri` that the caller must follow to complete authentication; the account is finalized after the realm round-trip. Otherwise, the request body must include `email`, `given_name`, `surname`, `password`, and `code`.

Only one Cogniac user may exist per email address. Attempts to create an account for an existing email are rejected.

**Auth:** no auth required

**Request body:** [CreateUserSchema](#schema-createuserschema) plus the user profile fields from [UserSchema](#schema-userschema) (`email`, `given_name`, `surname`, `password`).

**Response:** [UserSchema](#schema-userschema), or `{"redirect_uri": "..."}` when the invitation requires authentication via a third-party identity provider.

### `POST /1/users/{id}`

**update specified user ID**

Update mutable fields on the user record. Callers may update their own account; `tenant_admin` may update other users in their tenant. The path accepts the literal `current` as a shortcut for the authenticated user.

Updatable fields: `given_name`, `surname`, `password`. The `email` field cannot be changed. If multi-factor authentication is enabled on the account, MFA must be disabled before the user can be reassigned to a different authentication realm.

**Auth:** Bearer JWT; required roles: `{tenant_admin}` (caller targeting their own user record may call without the role)

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target user id, or `current` for the authenticated user. |

**Response:** [UserSchema](#schema-userschema)

### `DELETE /1/users/{id}`

**Remove the specified user from all tenants and delete the user from the system**

Permanently delete the user. The caller may delete their own account; `tenant_admin` may delete other users. Deletion removes the user from every tenant they belong to. The literal `current` resolves to the authenticated user, but passing the explicit user id is recommended to avoid accidental self-deletion.

Returns `204 No Content` on success.

**Auth:** Bearer JWT; required roles: `{tenant_admin}` (caller targeting their own user record may call without the role)

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target user id, or `current` for the authenticated user. |

### `GET /1/users/{user_id}/tenants`

**Get all the tenants that a user is authorized to access**

Currently only "current" as user_id is supported.

For each tenant the response carries the `tenant_id`, `name`, the caller's `roles` within that tenant, and the tenant's `contract_end_date` (Unix epoch seconds, or `null` if unset).

**Auth:** HTTP Basic, API key, or Bearer JWT for the authenticated user

**Path params:**

| Name | Type | Description |
|---|---|---|
| `user_id` | string | Must be `current` or the authenticated user's own id. |

**Response:**

```json
{
  "tenants": [
    {
      "tenant_id": "string",
      "name": "string",
      "roles": ["tenant_admin"],
      "contract_end_date": 1700000000
    }
  ]
}
```

### `POST /1/users/{user_id}/apiKeys`

**create user api key**

Provision a new API key for the user. API keys may be used in place of username + password for programmatic access (typically for SDK/script usage). The response is the only opportunity to retrieve the secret `api_key` value — subsequent GET calls return the key metadata without the secret.

Callers may only create keys for their own user record.

A free-form `description` is required; pick something that identifies where the key will be used.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `user_id` | string | Must be the authenticated user's id. |

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `description` | string | yes | Human-readable label for the key. |

**Response:** [ApiKeySchema](#schema-apikeyschema). The `api_key` field is populated only on this create call.

### `GET /1/users/{user_id}/apiKeys`

**get all user api keys**

List the user's API keys. The secret `api_key` value is never included in the response; only metadata (`key_id`, `description`, `created_at`, `last_auth`, etc.) is returned.

Callers may only list keys for their own user record.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `user_id` | string | Must be the authenticated user's id. |

**Response:** `{"data": [ApiKeySchema, ...]}` — see [ApiKeySchema](#schema-apikeyschema).

### `GET /1/users/{user_id}/apiKeys/{key_id}`

**Get one of the user's API keys**

Retrieve metadata for a single API key. The secret `api_key` value is not returned.

Callers may only retrieve keys for their own user record.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `user_id` | string | Must be the authenticated user's id. |
| `key_id` | string | Identifier of the API key. |

**Response:** [ApiKeySchema](#schema-apikeyschema)

### `DELETE /1/users/{user_id}/apiKeys/{key_id}`

**Deletes an API key**

Revoke an API key. Subsequent requests authenticated with the revoked key will fail.

Callers may only delete keys for their own user record.

Returns `204 No Content` on success.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `user_id` | string | Must be the authenticated user's id. |
| `key_id` | string | Identifier of the API key to delete. |

### `POST /1/users/requestPasswordReset`

**Reset the user password. Authentication is handled with the password**

reset token embedded in the password reset URI sent to a user.

Initiates a password reset by emailing a reset link to the address associated with the given user. The link contains a single-use token that the caller submits to `POST /1/users/submitPasswordReset` to set a new password.

For privacy this endpoint returns `200` whether or not the supplied identifier corresponds to a real account. Machine users cannot reset their password by this flow — they must authenticate using an API key.

**Auth:** no auth required

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | yes | Email address (or user id) of the account to reset. |

### `POST /1/users/submitPasswordReset`

**Validate token is email reset token and then change the password**

Complete a password reset using the token delivered in the email from `POST /1/users/requestPasswordReset`. On success the user's password is updated and any prior failed-authentication counters for the account are cleared.

Returns `204 No Content` on success.

**Auth:** no auth required

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `token` | string | yes | Single-use reset token from the password reset email. |
| `password` | string | yes | New password to set on the account. |

### `GET /1/users/{id}/pushNotifications`

Cogniac mobile app only. See `POST /1/users/{id}/pushNotifications` for input/output details.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | User id of the device owner. |

### `POST /1/users/{id}/pushNotifications`

**Create/Update user push notification endpoint for a given device**

Register a mobile device with Cogniac so that the user can receive push notifications. Intended for use by the Cogniac mobile applications, not for general API integrations.

Inputs (query parameters):

- `app_bundle_id` *(required)* — string identifying the Cogniac mobile app bundle.
- `device_id` *(required)* — unique identifier for the device.
- `token` *(required on create)* — push notification token assigned by the platform notification service.
- `enabled` *(optional, default `true`)* — whether push notifications are enabled for this device.
- `device_data` *(optional)* — opaque map of device information to associate with the registration.

Returns the resulting registration record (`app_bundle_id`, `device_id`, `enabled`, `custom_data`). See [PushRequestSchema](#schema-pushrequestschema).

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | User id of the device owner. |

### `DELETE /1/users/{id}/pushNotifications`

**Remove all push notification endpoints for the given user device**

Inputs (query parameters):

- `app_bundle_id` *(required)* — string identifying the Cogniac mobile app bundle.
- `device_id` *(required)* — unique device id.

Returns `204 No Content` on success.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | User id of the device owner. |

### `GET /1/users/{id}/invites`

**Returns a list of the "pending" invitations to a tenant for a user**

List the user's pending tenant invitations. Each item describes the tenant the user has been invited to, the role they will receive on acceptance, and the invitation timestamps. Callers may only list invitations addressed to themselves.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target user id, or `current` for the authenticated user. |

**Response:** array of [InvitationSchema](#schema-invitationschema).

### `POST /1/users/{id}/invites`

**Updates an invitation sent to a specified user**

This endpoint can be issued by a user to accept or decline an
invitation that's been sent to them.

This request will only be fulfilled if the requesting user is the
invited user. No other user can accept or decline the invitation on
behalf of the user.

Set `invitation_status` to `accepted` or `declined`; any other value is rejected. On `accepted`, the user is added to the tenant identified by `tenant_id` with the role recorded on the invitation. Expired invitations are cleared as a side-effect.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `id` | string | Target user id, or `current` for the authenticated user. |

**Request body:** [InvitationSchema](#schema-invitationschema) — at minimum `tenant_id` and `invitation_status`.

## Schemas

### `PushRequestSchema` <a id='schema-pushrequestschema'></a>

Mobile-app push-notification registration. Used by the Cogniac mobile applications.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `app_bundle_id` | string | **yes** |  | Identifier for the Cogniac mobile app bundle. |
| `device_id` | string | **yes** |  | Unique identifier for the user's device. |
| `token` | string | no | default=None | Push notification token assigned by the device platform's notification service. Required when creating a new registration. |
| `device_data` | any \| null | no | default=None | Optional opaque map of device information to associate with the registration (e.g. device type, OS). |
| `enabled` | boolean | no | default=True | Whether push notifications are enabled for this device. |
| `custom_data` | any | no |  | Map of additional data associated with the registration; returned on read. |

### `ApiKeySchema` <a id='schema-apikeyschema'></a>

A user API key. The secret value (`api_key`) is returned only at creation time; subsequent reads omit it.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `key_id` | string | no |  | Stable identifier for the key; safe to log and to use in URLs. |
| `user_id` | string | no |  | Owner of the key. |
| `email` | string | no |  | Email of the user who owns the key. |
| `last_auth` | integer | no |  | Unix epoch seconds of the most recent successful authentication using this key, or null if never used. |
| `created_at` | integer | no |  | Unix epoch seconds at which the key was issued. |
| `description` | string | no |  | Caller-supplied label describing the key's intended use. |
| `api_key` | string | no |  | The secret key value, in `{key_id}:{secret}` form. Returned only in the response to key creation; never returned on subsequent reads. |

### `InvitationSchema` <a id='schema-invitationschema'></a>

A pending invitation for a user to join a tenant.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `invited_user_email` | string (email) | no |  | Email address that was invited. |
| `created_at` | number | no |  | Unix epoch seconds at which the invitation was issued. |
| `created_by` | string | no |  | Email of the user who issued the invitation. |
| `invitation_status` | string | no | default='pending' | One of `pending`, `accepted`, `declined`. Set this field on `POST /1/users/{id}/invites` to accept or decline. |
| `tenant_id` | string | no |  | Tenant the user is being invited to join. |
| `register_url` | string \| null | no |  | URL the invitee should follow to register, when a custom registration landing page is in use. |
| `tenant_name` | string | no |  | Display name of the inviting tenant. |
| `invitation_url` | string | no |  | URL embedded in the invitation email; the invitee follows this link to accept. |
| `accepted_at` | number | no |  | Unix epoch seconds at which the invitation was accepted, if any. |
| `resend_counter` | integer | no |  | Number of times the invitation email has been resent. |
| `last_resend_at` | number | no |  | Unix epoch seconds of the most recent resend. |
| `last_resend_by` | string (email) | no |  | Email of the user who triggered the most recent resend. |
| `code` | string | no |  | Single-use invitation code; required on `POST /1/users` to accept the invitation. |
| `role` | string | no | default='tenant_user' | Invited user's initial tenant role. |
| `realm_id` | string | no | default=None | Indicates the realm to use to authenticate the invited user. If unset or `None`, then the default Cogniac authentication realm will be used. If set, the user will be redirected to the identity provider to authenticate when creating their Cogniac account. |
| `invited_user` | [UserSchema](#schema-userschema) | no | default=None | User information stored when they initiate user creation by accepting a user invitation and their invitation is associated with a third-party identity provider. |

### `AuthenticateRedirectQuerySchema` <a id='schema-authenticateredirectqueryschema'></a>

Query parameters used when account creation is bound to a third-party identity provider and the caller must be redirected to the realm to authenticate.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `tenant_id` | string | no |  | Tenant the user is joining. |
| `invite_code` | string | no |  | Invitation code that grants access to the tenant. |
| `callback_url` | string | no |  | URL the realm should redirect to after authentication completes. |

### `CreateUserSchema` <a id='schema-createuserschema'></a>

Request body for `POST /1/users`. Combined with the profile fields from [UserSchema](#schema-userschema) (`email`, `given_name`, `surname`, `password`).

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `email` | string | no | default=None | Email address for the new account. Must match the address that was invited. |
| `code` | string | no | default=None | Invitation code from the invitation email. Required unless creating via a referral. |
| `machine_user` | boolean | no | default=False | Used for creating machine users. |
| `roles` | list[any] | no |  | System roles to grant when provisioning a machine user. |
| `referral_id` | string \| null | no | default=None | Onboarding referral ID |
| `tenant_id` | string \| null | no | default=None | Tenant the user is joining. Required when `referral_id` is supplied; otherwise inferred from the invitation. |

### `UserSchema` <a id='schema-userschema'></a>

A Cogniac user record.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `user_id` | string | no |  | Stable identifier for the user. |
| `email` | string | no | default=None | Email address; serves as the login identifier. Immutable after account creation. |
| `password` | string | no | default=None | Password. Write-only — accepted on create/update, never returned. |
| `given_name` | string | no | default=None | First name. |
| `surname` | string | no | default=None | Last name. |
| `machine_user` | boolean \| null | no | default=False | `true` for service accounts that authenticate only with an API key. Settable only on machine-user provisioning; mutually exclusive with the invitation-accept flow. |
| `created_at` | number | no | default=None | Unix epoch seconds at which the account was created. |
| `modified_at` | number | no | default=None | Unix epoch seconds at which the account was last modified. |
| `last_auth` | number | no |  | Unix epoch seconds of the most recent successful authentication. |
| `password_modified_at` | number | no | default=None | Unix epoch seconds at which the password was last changed. |
| `tenant_name` | string | no |  | Display name of the tenant when the record is returned in a tenant context. |
| `status` | string | no |  | Account status (e.g. `ENABLED`). |
| `default_region` | string | no | default=None | The user's default Cogniac deployment region. |
| `custom_data` | any \| null | no |  | Caller-defined metadata associated with the user. |
| `title` | string | no |  | Job title. |
| `code` | string | no | default=None | Invitation code, accepted on account creation. |
| `mfa_active` | list[any] | no |  | Multi-factor authentication state. |
| `realm_id` | string | no | default=None | The realm that the user will use to authenticate, if any. |
| `roles` | list[any] \| null | no |  | System roles assigned to the user. For invitation acceptance, roles are taken from the server-side invitation record and are not settable from the request body. For machine-user provisioning, the only system role a caller may assign is `meraki_admin`. |
| `api_key` | [ApiKeySchema](#schema-apikeyschema) | no |  | Used only when provisioning machine users. |
| `first_login` | boolean | no | default=False | `true` on the response when this is the user's first successful login. |
