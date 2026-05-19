# ticket-core-api

Submit a Cogniac support ticket from inside the customer's Cogniac UI. The service is a thin authenticated proxy: it takes the description and metadata supplied by the signed-in user, stamps the request with the caller's identity (email and full name resolved from the bearer token), and forwards it to the Cogniac Freshdesk help desk. The response from Freshdesk is returned to the caller verbatim, so the UI can surface the newly-created ticket id and status directly.

There is exactly one operation. The endpoint is unavailable in on-prem deployments.

## Endpoints

### `POST /1/ticket`

**Submit a support ticket**

Create a Freshdesk support ticket on behalf of the signed-in user.

The caller supplies the ticket payload (typically a `subject`, a `description`, and any priority/category fields the UI exposes). The service looks up the user record associated with the bearer token, stamps the request with the user's `email` and full `name`, and forwards the result to the Cogniac Freshdesk tenant. Freshdesk's response body, status code, and `Content-Type` flow back to the caller unchanged.

The endpoint is not exposed in on-prem deployments — the route is only registered when the service is running in a cloud environment.

**Auth:** Bearer JWT required

**Errors:**
- `401` — missing or invalid Bearer token in the Authorization header.
- `403` — token rejected by the authorization layer (e.g. revoked or permission denied).
- Other status codes — the response is whatever Freshdesk returned for the upstream `POST /api/v2/tickets` call, including its body and `Content-Type`. Consult Freshdesk's ticket-creation documentation for the upstream contract.

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `authorization` | header | string | **yes** | `Bearer <jwt>` |

**Request body** (`application/json`, required: **yes**):

The body is forwarded to Freshdesk after the service overwrites the `email` and `name` fields with the authenticated user's identity. Any `email` or `name` supplied by the client is ignored. All other fields accepted by the Freshdesk Create-Ticket API may be supplied (for example `subject`, `description`, `priority`, `status`, `tags`, `custom_fields`).

**Responses:**

The response status, body, and `Content-Type` are proxied from Freshdesk. On success, expect a JSON document describing the created ticket.
