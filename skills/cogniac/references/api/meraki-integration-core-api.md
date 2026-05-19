# meraki-integration-core-api

Proxies requests from a Cogniac tenant to the Cisco Meraki dashboard API. The Cogniac tenant must be provisioned with the Meraki integration feature and configured with a Meraki dashboard API key and organization. See the Meraki API Advanced Setup Guide for the prerequisite tenant configuration steps; contact your Cogniac account team if the Integrations section is not present on your tenant Settings page.

## Using the proxy

Send requests to `/1/meraki/{urlsuffix}` exactly as you would send them to the upstream Meraki dashboard API, but:

- Authenticate with a Cogniac Bearer JWT for the tenant (the `Authorization: Bearer <token>` header used everywhere else in the Cogniac API). Do **not** send `X-Cisco-Meraki-API-Key` — the proxy injects the tenant's configured Meraki API key on your behalf.
- Replace the Meraki host and version prefix `https://api.meraki.com/api/v1` with the Cogniac base URL plus `/1/meraki`. The `{urlsuffix}` you supply is the path that would otherwise follow `/api/v1/` in a direct Meraki call. For example, the Meraki call `GET https://api.meraki.com/api/v1/organizations` becomes `GET {cogniac-base}/1/meraki/organizations`.
- For convenience, the proxy also accepts a `urlsuffix` that already contains a leading `api/v1/` segment; in that case the segment is preserved as-is.
- Query string parameters, request bodies (`application/json` or otherwise), and most request headers are forwarded unchanged. The response status code, body, and headers from Meraki are returned to the caller as-is, with hop-by-hop headers (`content-encoding`, `content-length`, `transfer-encoding`, `connection`) stripped.

The set of operations available through the proxy is exactly the set defined by the upstream Cisco Meraki dashboard API. Refer to Cisco's Meraki Dashboard API documentation for the available endpoints, request shapes, and response shapes.

### Authorization and scope

All four methods require a valid Cogniac Bearer JWT scoped to the tenant whose Meraki integration should be used. Requests are executed against the Meraki organization configured on that tenant; there is no way to target a different organization through this proxy. If the tenant is not configured with a Meraki dashboard API key, the request fails.

### Errors

In addition to any status code that Meraki itself returns, the proxy can return a `5xx` server error if the upstream Meraki request fails at the transport level (connection error, timeout, invalid headers, or other request exception). Standard Cogniac authentication errors (`401`/`403`) apply to the inbound Bearer token.

## Endpoints

### `GET /1/meraki/{urlsuffix}`

**Meraki Proxy**

Forwards a `GET` request to the tenant's Meraki dashboard API. Use for all read operations defined by the upstream Meraki API (for example, listing organizations, networks, devices, or cameras).

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `urlsuffix` | string | Path segment(s) appended to the Meraki dashboard API base (`https://<meraki-host>/api/v1/`). May span multiple `/`-separated segments (e.g. `organizations/{organizationId}/networks`). Include any query string normally. |

### `DELETE /1/meraki/{urlsuffix}`

**Meraki Proxy**

Forwards a `DELETE` request to the tenant's Meraki dashboard API. Use for resource-removal operations defined by the upstream Meraki API.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `urlsuffix` | string | Path segment(s) appended to the Meraki dashboard API base (`https://<meraki-host>/api/v1/`). May span multiple `/`-separated segments. |

### `POST /1/meraki/{urlsuffix}`

**Meraki Proxy**

Forwards a `POST` request to the tenant's Meraki dashboard API. The request body is forwarded unchanged; set `Content-Type` (typically `application/json`) as required by the upstream operation.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `urlsuffix` | string | Path segment(s) appended to the Meraki dashboard API base (`https://<meraki-host>/api/v1/`). May span multiple `/`-separated segments. |

### `PUT /1/meraki/{urlsuffix}`

**Meraki Proxy**

Forwards a `PUT` request to the tenant's Meraki dashboard API. The request body is forwarded unchanged; set `Content-Type` (typically `application/json`) as required by the upstream operation.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `urlsuffix` | string | Path segment(s) appended to the Meraki dashboard API base (`https://<meraki-host>/api/v1/`). May span multiple `/`-separated segments. |
