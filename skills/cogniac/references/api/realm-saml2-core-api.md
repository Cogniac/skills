# realm-saml2-core-api

Handles SAML 2.0 single sign-on (SSO) and single logout (SLO) for Cogniac authentication realms. A realm represents a tenant's external Identity Provider (IdP) — typically Okta, Azure AD, ADFS, or similar — bound to Cogniac as the Service Provider (SP).

Most endpoints here are not called directly by an integrator; they are browser-driven URLs that participate in the SP-initiated SAML 2.0 flow. Customer SSO administrators configuring a realm receive SP metadata from Cogniac out-of-band during realm provisioning.

## Endpoints

### `GET /1/realms/{realm_id}/authenticate`

**Initiates authentication flow for the specified authentication realm**

When trying to authenticate a user with a third-party authentication
realm (i.e., `realm_id != None` for the `User` item),
the user agent (browser) should redirect to this URL, which will
look up the user, and if they have an authentication realm specified,
return a redirection to the realm's authentication page.

This is the SP-initiated SSO entry point. The response carries a SAML `AuthnRequest` bound for the realm's configured IdP (HTTP-POST binding), which the user agent forwards to the IdP for credential collection. After the user authenticates with the IdP, the IdP posts the SAML assertion back to the ACS endpoint (`POST /1/realms/{realm_id}/saml/post`).

The optional `callback_url` query parameter is preserved across the round-trip and used as the post-login redirect target for the user agent. `tenant_id` and `invite_code` are supplied only when a brand-new user is accepting a tenant invitation that requires SAML authentication; for existing users they are omitted.

Returns a cache-suppressed (`Cache-Control: no-cache, no-store`) HTML form auto-submitted to the IdP.

**Auth:** no auth required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `realm_id` | string | Identifier of the realm whose IdP should authenticate the user. |

**Query params:** see [AuthenticateRedirectQuerySchema](#schema-authenticateredirectqueryschema).

### `POST /1/realms/{realm_id}/saml/post`

**Handle ACS POST from SAML IdP**

The SAML 2.0 Assertion Consumer Service (ACS) endpoint. The IdP delivers its signed `Response` document here via HTTP-POST binding after authenticating the user. Cogniac validates the assertion against the realm's outstanding `AuthnRequest`, extracts the user identity (`NameID`), and either:

- redirects the user agent back to the original `callback_url` with a Cogniac access token appended as query parameters (for existing users), or
- creates a new Cogniac user account from a pending tenant invitation matching the realm and the asserted email, then redirects with a token (for invited first-time users).

This endpoint is invoked by the IdP — not by integrators — as part of the SP-initiated SSO browser flow. The request body is a standard SAML 2.0 `application/x-www-form-urlencoded` payload containing the Base64-encoded `SAMLResponse` form field.

**Auth:** no auth required (authentication is established by validating the SAML assertion)

**Path params:**

| Name | Type | Description |
|---|---|---|
| `realm_id` | string | Identifier of the realm whose IdP issued the assertion. |

**Errors:**
- `4xx` / `5xx` — the SAML response could not be validated against the realm's outstanding authentication requests, or no matching tenant invitation exists for a first-time user.

### `GET /1/realms/{realm_id}/saml/logout/redirect`

**Initiates SAML 2.0 Single Logout (SLO) for the caller's realm session**

SP-initiated Single Logout entry point. The user agent navigates here with the caller's Cogniac access token in the `token` query parameter. Cogniac decodes the token to recover the realm session, deletes the local SP session, then issues a SAML `LogoutRequest` to the realm's IdP via HTTP-POST binding so the IdP can terminate its session as well.

After the IdP processes the logout (and any further SLO callbacks), the user agent is redirected to `callback_url` (default: the Cogniac web app login page).

**Auth:** no auth required; the supplied `token` query parameter must be a valid Cogniac access token

**Path params:**

| Name | Type | Description |
|---|---|---|
| `realm_id` | string | Identifier of the realm whose IdP should terminate the session. |

**Query params:** see [LogoutRedirectQuerySchema](#schema-logoutredirectqueryschema).

### `POST /1/realms/{realm_id}/saml/logout/post`

**Handle SLO POST from SAML IdP**

The SAML 2.0 Single Logout receiver endpoint. The IdP posts a `LogoutRequest` (IdP-initiated SLO) or `LogoutResponse` (response to an SP-initiated SLO) here via HTTP-POST binding. Cogniac parses the SAML document and redirects the user agent to the realm's configured post-logout URL (falling back to the Cogniac web app logout/login page).

Invoked by the IdP — not by integrators.

**Auth:** no auth required (authentication is established by validating the SAML message)

**Path params:**

| Name | Type | Description |
|---|---|---|
| `realm_id` | string | Identifier of the realm whose IdP is issuing the logout. |

### `GET /1/login/redirect`

**Returns the authentication flow entrypoint for a given email address**

Resolves the correct login entry point for the supplied email. If the email belongs to a user whose tenant is bound to a SAML realm, the response carries a `redirect_uri` pointing at that realm's `authenticate` endpoint (kicking off SP-initiated SSO). Otherwise, the response points at the standard password login page with the email pre-filled.

Use this from a login page to route users to the appropriate authentication flow.

**Response:** JSON object with a single field, `redirect_uri` (string), to which the user agent should navigate.

**Auth:** no auth required

**Query params:** see [LoginRedirectQuerySchema](#schema-loginredirectqueryschema).

### `GET /1/logout/redirect`

**Returns the logout flow entrypoint for the authenticated caller**

Resolves the correct logout entry point for the authenticated user. If the caller's account is bound to a SAML realm, the response carries a `redirect_uri` pointing at that realm's SLO endpoint (kicking off SP-initiated SAML Single Logout). Otherwise, the response points at the supplied `callback_url` (default: the Cogniac web app login page).

**Response:** JSON object with a single field, `redirect_uri` (string), to which the user agent should navigate.

**Auth:** Bearer JWT required

## Schemas

### `LoginRedirectQuerySchema` <a id='schema-loginredirectqueryschema'></a>

Query parameters for `GET /1/login/redirect`.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `email` | string | **yes** |  | Email address of the user whose login entry point should be resolved. |
| `callback_url` | string | no |  | URL the user agent should ultimately land on after authentication. Defaults to the Cogniac web app login page. |

### `AuthenticateRedirectQuerySchema` <a id='schema-authenticateredirectqueryschema'></a>

Query parameters for `GET /1/realms/{realm_id}/authenticate`.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `tenant_id` | string | no |  | Tenant the invited user is joining. Supplied only when a first-time user is accepting a tenant invitation; omitted for existing users. |
| `invite_code` | string | no |  | Tenant invitation code accompanying `tenant_id`. Supplied only during first-time user onboarding. |
| `callback_url` | string | no |  | URL the user agent should land on after the SSO round-trip completes. Defaults to the Cogniac web app login page. |

### `LogoutRedirectQuerySchema` <a id='schema-logoutredirectqueryschema'></a>

Query parameters for `GET /1/realms/{realm_id}/saml/logout/redirect`.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `token` | string | **yes** |  | Cogniac access token identifying the realm session to terminate. |
| `callback_url` | string | no |  | URL the user agent should land on after Single Logout completes. Defaults to the Cogniac web app login page. |
