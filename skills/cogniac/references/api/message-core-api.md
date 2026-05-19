# message-core-api

Attach short text messages to Cogniac platform objects — media items, subjects, and applications — and optionally tag other users in the same tenant. Messages support lightweight collaboration and annotation alongside detection workflows without modifying the underlying object.

All endpoints require Bearer-token authentication. Messages are scoped to the caller's tenant; a message can only be read by, and tagged users must belong to, that same tenant.

## Endpoints

### `POST /1/messages`

**Create a message**

Post a new message in the caller's tenant. Every message must carry the free-form `message` text and the `media_id` of the media item the message is associated with. Optionally bind the message to a `subject_uid` and/or `app_id` to scope it to a specific subject or application context, and supply `focus` to attach a region-of-interest payload.

To notify other users in the tenant, list their email addresses in `tag_users`. Each tagged user is indexed so that subsequent searches with `tagged_user=true` will return the message for that user. All tagged users must belong to the same tenant as the caller.

The server assigns the `message_id` and `timestamp`; both are returned in the response.

**Auth:** Bearer JWT required

**Request body** (`application/json`, required: **yes**): [CreateMessageRequestSchema](#schema-createmessagerequestschema)

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | `application/json` → [MessageResponseSchema](#schema-messageresponseschema) |

### `GET /1/messages`

**Search for messages**

Return messages in the caller's tenant, optionally filtered by media item, subject, application, authorship, or tag membership. With no filter, returns every message in the tenant.

Supported query parameters are described in [SearchMessagesRequestSchema](#schema-searchmessagesrequestschema). Filters compose: for example, supplying both `media_id` and `app_id` narrows results to messages that match both. Setting `from_user=true` restricts results to messages posted by the calling user; `tagged_user=true` restricts to messages in which the calling user was tagged.

Results are returned in timestamp order. Pass `reverse=true` to sort from newest to oldest. Use `limit` to cap the page size (1–1000) and pass the `last_key` from a prior response to fetch the next page. When the final page has been returned, `last_key` in the response will be `null`.

**Auth:** Bearer JWT required

**Query parameters:** see [SearchMessagesRequestSchema](#schema-searchmessagesrequestschema).

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response — `data` is a list of [MessageResponseSchema](#schema-messageresponseschema) items; `last_key` is an opaque pagination cursor or `null` when there are no more results. | `application/json` |

## Schemas

### `CreateMessageRequestSchema` <a id='schema-createmessagerequestschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `message` | string | **yes** |  | Free-form message text. |
| `media_id` | string | **yes** |  | Identifier of the media item the message is associated with. |
| `subject_uid` | string \| null | no | default=None | Optional subject the message is associated with. |
| `app_id` | string \| null | no | default=None | Optional application the message is associated with. |
| `focus` | any \| null | no |  | Optional region-of-interest or focus payload to attach to the message. |
| `tag_users` | list[string (email)] | no |  | List of user email addresses to tag (must be in same tenant). |

### `MessageTableSchema` <a id='schema-messagetableschema'></a>

Stored representation of a message. Returned as the body of [MessageResponseSchema](#schema-messageresponseschema) entries.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `tenant_id` | string | **yes** |  | Tenant the message belongs to. |
| `message_id` | string | **yes** |  | Server-assigned identifier for the message. |
| `tenant_id_from_user_email` | string | **yes** |  | Composite key identifying the tenant and the author's email; used to look up messages by author within a tenant. |
| `timestamp` | number | **yes** |  | Server-assigned creation time, in seconds since the Unix epoch. |

### `MessageResponseSchema` <a id='schema-messageresponseschema'></a>

Response body returned for a single message. Carries the fields of the created or retrieved message, including the server-assigned `message_id` and `timestamp` along with the request fields supplied at creation time.

_No fields detected._

### `TaggedUserMessageTableSchema` <a id='schema-taggedusermessagetableschema'></a>

Record linking a tagged user to a message. One record exists for each user tagged in a given message; used to drive the `tagged_user=true` search filter.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `tenant_id_tagged_user_email` | string | **yes** |  | Composite key identifying the tenant and tagged user's email. |
| `tagged_user_email` | string (email) | **yes** |  | Email address of the tagged user. |
| `message_id` | string | **yes** |  | Identifier of the message in which the user was tagged. |
| `tenant_id` | string | **yes** |  | Tenant the message belongs to. |
| `timestamp` | number | **yes** |  | Creation time of the underlying message, in seconds since the Unix epoch. |

### `SearchMessagesRequestSchema` <a id='schema-searchmessagesrequestschema'></a>

Query parameters accepted by `GET /1/messages`. All fields are optional; when none are supplied, every message in the caller's tenant is returned.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `media_id` | string \| null | no | default=None | Return only messages associated with this media item. |
| `subject_uid` | string \| null | no | default=None | Return only messages associated with this subject. |
| `app_id` | string \| null | no | default=None | Return only messages associated with this application. |
| `from_user` | boolean | no | default=False | If `true`, return only messages posted by the user making this call. |
| `tagged_user` | boolean | no | default=False | If `true`, return only messages in which the user making this call was tagged. |
| `reverse` | boolean | no | default=False | If `true`, sort results from newest to oldest. |
| `last_key` | string \| null | no | default=None | Opaque pagination cursor from a prior response. Omit to start from the first page. |
| `limit` | number \| null | no | default=None; range(min=1, max=1000) | Maximum number of messages to return in a single page. |
