# media-embedding-core-api

Compute and serve image embeddings for the Cogniac labeling pipeline. The service runs a media item through the image-encoder half of a segmentation model (the "labeling image encoder") and returns a compact float16 vector that downstream clients pair with a labeling mask-decoder model to interactively segment objects in the image. It also serves the matching mask-decoder model file itself, so labeling clients can run decoder inference locally once they have the encoder embedding.

Two related operations are exposed under the `/22` API version prefix:

- Embedding generation: callers submit a `media_id` (and an optional `focus` region of the image). The service downloads the media, runs the resolved encoder model, returns the embedding as a base64-encoded byte buffer plus its `shape` and `data_type`, and caches the result so subsequent requests for the same `(model, media, focus)` triple return immediately.
- Mask-decoder model retrieval: callers fetch the ONNX mask-decoder model that pairs with the encoder embedding so they can run interactive decoding client-side.

The service is intended for use by Cogniac labeling tools rather than general application traffic; most endpoints are restricted to internal Cogniac staff. Each endpoint requires a tenant-scoped Bearer token, and the per-application embedding endpoint additionally requires the caller's user email to be on the Cogniac internal allowlist.

## Endpoints

Grouped by tag.

### `Labeling Image Encoder Models`

#### `POST /22/applications/{app_id}/labelingImageEncoderModel` <a id='op-get-labeling-image-encoder-model-embedding-22-applications--app-id--labelingimageencodermodel-post'></a>
**Get an image embedding for an application's active labeling encoder model**

Compute an image embedding for `media_id` using the image-encoder model that pairs with the application's currently active labeling mask-decoder model. The caller supplies the `labeling_mask_decoder_model_id` they intend to run client-side; the service verifies this matches the application's active mask-decoder model and resolves the paired encoder model from it.

Embeddings are cached, so repeated calls for the same `(model, media_id, focus)` triple return without re-running inference. The response carries the embedding as a base64-encoded byte buffer along with its tensor `shape` and `data_type` (`float16`) so the client can reconstruct the array and feed it into the mask-decoder model.

**Auth:** Bearer JWT; required roles: `{cogniac_admin}`

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `app_id` | path | string | **yes** | Identifier of the application whose active labeling model should be used. |

**Request body** (`application/json`, required: **yes**): [GetAppMediaEmbeddingRequest](#schema-getappmediaembeddingrequest)

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | `application/json` → [GetAppMediaEmbeddingResponse](#schema-getappmediaembeddingresponse) |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 400 | Media could not be retrieved, the supplied `labeling_mask_decoder_model_id` does not match the application's active mask-decoder model, or the resolved encoder model has no inference endpoint available. |
| 404 | The caller's user account is not on the Cogniac internal allowlist, the application has no active labeling model configured, or the resolved encoder model is unknown. |
| 503 | The mask-decoder model or its paired image-encoder model is not currently available for the application. The response includes `Retry-After: 1`. |

#### `GET /22/media/{media_id}/embeddings` <a id='op-get-media-embeddings-22-media--media-id--embeddings-get'></a>
**Get an image embedding for a specific encoder model**

Compute an image embedding for `media_id` using the explicit encoder model named by `model_id`. Use this endpoint when the caller already knows which encoder model to invoke (for example, when pinning to a specific model revision); use the application-scoped `POST` variant when the encoder should be resolved from the application's currently active labeling model instead.

Embeddings are cached on a `(model_id, media_id, focus)` key, so repeated calls return without re-running inference. The response carries the embedding as a base64-encoded byte buffer along with its tensor `shape` and `data_type` (`float16`).

**Auth:** Bearer JWT required

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `media_id` | path | string | **yes** | Identifier of the media item to embed. |
| `model_id` | query | string | **yes** | Identifier of the image-encoder model to run. |
| `focus` | query | string \| null | no | Optional region of interest within the media. The same `focus` value must be supplied on subsequent requests to hit the cache. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | `application/json` → [GetMediaEmbeddingResponse](#schema-getmediaembeddingresponse) |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 400 | The media item could not be retrieved. |

### `Labeling Mask Decoder Models`

#### `GET /22/applications/{application_id}/labelingMaskDecoderModel` <a id='op-get-labeling-mask-decoder-model-file-22-applications--application-id--labelingmaskdecodermodel-get'></a>
**Download the application's active mask-decoder model in ONNX format**

Stream the ONNX mask-decoder model that pairs with the application's currently active labeling model. The response is the raw ONNX bytes extracted from the model package, with `Content-Disposition: attachment` set so HTTP clients save it under the model identifier as the filename. Use the embedding endpoints above to obtain the encoder output that this decoder consumes.

**Auth:** Bearer JWT required

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `application_id` | path | string | **yes** | Identifier of the application whose active labeling model should be downloaded. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | `application/json` → any |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 404 | The model package is missing its `config.json`, or the ONNX model file named in the package config could not be located inside the archive. |
| 503 | The application has no active labeling model configured. The response includes `Retry-After: 1`. |

#### `HEAD /22/applications/{application_id}/labelingMaskDecoderModel` <a id='op-get-labeling-mask-decoder-model-file-22-applications--application-id--labelingmaskdecodermodel-head'></a>
**Probe for the application's active mask-decoder model**

Probe whether an active mask-decoder model is configured for the application without downloading its bytes. The response carries a `Content-Disposition` header naming the active model identifier. Use this to cheaply check the currently active model before issuing the matching `GET`.

**Auth:** Bearer JWT required

**Parameters:**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `application_id` | path | string | **yes** | Identifier of the application to probe. |

**Responses:**

| Status | Description | Schema |
|---|---|---|
| 200 | Successful Response | `application/json` → any |
| 422 | Validation Error | `application/json` → [HTTPValidationError](#schema-httpvalidationerror) |

**Errors:**

| Status | Condition |
|---|---|
| 503 | The application has no active labeling model configured. The response includes `Retry-After: 1`. |

---

## Schema Components

All Pydantic-derived schemas referenced above. Constraints (enum, range, length, pattern, default) are inline so an API consumer can write a correct client without reading Pydantic source.

### `AppMediaEmbeddingDataTypeEnum` <a id='schema-appmediaembeddingdatatypeenum'></a>

**Enum:** 'float16'

### `GetAppMediaEmbeddingRequest` <a id='schema-getappmediaembeddingrequest'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `focus` | dict[str, any] \| null | no |  | Optional region of interest within the media. When set, the embedding is computed (and cached) for this focus region rather than the full image. |
| `labeling_mask_decoder_model_id` | string | **yes** |  | Identifier of the mask-decoder model the caller intends to use. Must match the application's currently active labeling model; otherwise the request is rejected. |
| `media_id` | string | **yes** |  | Identifier of the media item to embed. |

### `GetAppMediaEmbeddingResponse` <a id='schema-getappmediaembeddingresponse'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `data_type` | [AppMediaEmbeddingDataTypeEnum](#schema-appmediaembeddingdatatypeenum) | **yes** |  | Element type of the embedding tensor. Always `float16`. |
| `embedding` | string | **yes** |  | Base64-encoded contiguous byte buffer of the embedding tensor. Decode and interpret using `shape` and `data_type`. |
| `shape` | list[integer] | **yes** |  | Dimensions of the embedding tensor, in order. |

### `GetMediaEmbeddingResponse` <a id='schema-getmediaembeddingresponse'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `data_type` | [MediaEmbeddingDataTypeEnum](#schema-mediaembeddingdatatypeenum) | **yes** |  | Element type of the embedding tensor. Always `float16`. |
| `embedding` | string | **yes** |  | Base64-encoded contiguous byte buffer of the embedding tensor. Decode and interpret using `shape` and `data_type`. |
| `shape` | list[integer] | **yes** |  | Dimensions of the embedding tensor, in order. |

### `HTTPValidationError` <a id='schema-httpvalidationerror'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `detail` | list[[ValidationError](#schema-validationerror)] | no |  | One entry per validation failure. |

### `MediaEmbeddingDataTypeEnum` <a id='schema-mediaembeddingdatatypeenum'></a>

**Enum:** 'float16'

### `ValidationError` <a id='schema-validationerror'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `ctx` | object | no |  | Additional context attached to the validation error, if any. |
| `input` | any | no |  | The input value that failed validation. |
| `loc` | list[string \| integer] | **yes** |  | Path to the offending field in the request payload. |
| `msg` | string | **yes** |  | Human-readable description of the validation failure. |
| `type` | string | **yes** |  | Machine-readable validation-error code. |
