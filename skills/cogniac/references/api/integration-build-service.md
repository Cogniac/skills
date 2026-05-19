# integration-build-service

Build and manage integration containers from caller-supplied Python source. An integration build packages source code plus pinned `pip` requirements against an approved base image and produces a versioned, immutable artifact addressable by `build_id`. The resulting artifact is consumed downstream by EdgeFlow and CloudFlow deployments.

Builds are scoped to the caller's tenant. Each `name` is an independent build series; submitting a build with an existing `name` allocates the next sequential `version` for that name. A `build_id` has the form `"{name}:{version}"`.

## Endpoints

### `GET /1/builds/version`

Return the running service version string.

**Auth:** no auth required

### `GET /1/builds`

List integration builds in the caller's tenant, paginated and ordered by creation time.

Use `start`/`end` to bound the time window, `limit` to cap the page size, and `reverse=true` to walk newest-first. Filter to a single series with `name`, or by terminal outcome with `status`. When more results exist beyond the page, the response includes a `paging.next` URL pre-populated with the cursor for the following page.

**Auth:** Bearer JWT required

**Query params** map to [IntegrationBuildSearchSchema](#schema-integrationbuildsearchschema).

### `POST /1/builds`

Submit a new integration build.

Accepts the source code, pinned `pip` requirements, optional base image, and target Python runtime as JSON. The service validates the request, allocates the next `version` for the given `name` within the tenant, validates requested Python packages and base image against the tenant's approved-package policy, then builds and publishes the container image. The created build record is returned, including the resolved `image` reference and any `errors` captured during validation or build.

A `name` must consist of lowercase alphanumeric characters only. Non-ASCII source must declare a UTF-8 coding line per PEP 263 in its first or second line. Each entry in `requirements` must be a single line of the form `package==version`. If `base_image` is omitted the service selects an approved default based on `program_language` and whether the source imports `cv2`.

**Auth:** Bearer JWT required

**Request body:** [CreateIntegrationBuildSchema](#schema-createintegrationbuildschema) (`application/json`).

**Response:** [IntegrationBuildSchema](#schema-integrationbuildschema).

### `GET /1/builds/{build_id}`

Return a single integration build by `build_id`.

The `build_id` must be the `"{name}:{version}"` form returned at create time.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `build_id` | string | Build identifier of the form `"{name}:{version}"`. |

**Response:** [IntegrationBuildSchema](#schema-integrationbuildschema).

### `DELETE /1/builds/{build_id}`

Delete an integration build record by `build_id`.

Returns `204 No Content` on success.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `build_id` | string | Build identifier of the form `"{name}:{version}"`. |

### `GET /1/builds/names`

Return the set of distinct build `name` values present in the caller's tenant.

**Auth:** Bearer JWT required

**Response:** JSON array of strings.

### `POST /1/builds/lint/flake8`

Run `flake8` against a snippet of Python source and return its captured `stdout` and `stderr`. Use this to preflight source before submitting it to `POST /1/builds`.

**Auth:** Bearer JWT required

**Request body:** [LintFlake8RequestSchema](#schema-lintflake8requestschema).

**Response:** [LintFlake8ResponseSchema](#schema-lintflake8responseschema).

### `GET /1/builds/application/{app_id}`

Return builds for a given application.

Accepts `limit` (default `1`) and `reverse` (default `True`) as optional query
params. If `reverse` is set to `True` the builds will be returned for an
application in descending order.

The benefit of using this endpoint over `/1/builds/{build_id}` is that it
directly pulls the items for an application without needing to scan over
a time range and potentially reading items for other applications which
aren't needed.

**Auth:** Bearer JWT required

**Path params:**

| Name | Type | Description |
|---|---|---|
| `app_id` | string | Application identifier. |

**Query params** map to [ApplicationBuildSearchSchema](#schema-applicationbuildsearchschema).

## Schemas

### `IntegrationBuildSearchSchema` <a id='schema-integrationbuildsearchschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `start` | number | no | range(min=0) | Lower bound of the build creation timestamp window (epoch seconds). |
| `end` | number | no | range(min=0) | Upper bound of the build creation timestamp window (epoch seconds). Defaults to the current time. |
| `limit` | integer | no | default=100; range(min=1) | Maximum number of builds to return on this page. |
| `reverse` | boolean | no | default=False | When `true`, return results newest-first. |
| `name` | string \| null | no |  | Restrict results to a single build series by `name`. |
| `status` | string \| null | no | default='all'; one of {'success', 'failure', 'all'} | Filter by terminal outcome. `success` returns builds with no recorded errors; `failure` returns builds with errors. |

### `ApplicationBuildSearchSchema` <a id='schema-applicationbuildsearchschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `limit` | integer | no | default=1; range(min=1) | Maximum number of builds to return. |
| `reverse` | boolean | no | default=True | When `true`, return results newest-first. |

### `CreateIntegrationBuildSchema` <a id='schema-createintegrationbuildschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `name` | string | **yes** |  | Build series name. Must consist of lowercase alphanumeric characters only. Submitting against an existing `name` allocates the next sequential `version`. |
| `description` | string \| null | no | default=None | Free-text description of this build. |
| `src_code` | string | **yes** |  | Python integration source code. Non-ASCII source must include a PEP 263 UTF-8 coding declaration on the first or second line. |
| `requirements` | string \| null | no | default='' | Pinned `pip` requirements, one per line. Each line must be of the form `package==version`. |
| `base_image` | string \| null | no | default=None | Optional Docker base image reference. Must be an approved image for the caller's tenant. When omitted, the service selects an approved default based on `program_language` and whether the source imports `cv2`. |
| `program_language` | string | no | default='python3.10'; `OneOf` | Target Python runtime. One of `python2.7`, `python3.6`, `python3.10`. |

### `IntegrationBuildErrorSchema` <a id='schema-integrationbuilderrorschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `message` | string | no |  | Human-readable description of the validation or build failure. |
| `details` | object \| null | no |  | Optional structured detail payload accompanying `message`. |

### `IntegrationBuildSchema` <a id='schema-integrationbuildschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `build_id` | string | no |  | Build identifier of the form `"{name}:{version}"`. |
| `name` | string | no |  | Build series name. |
| `version` | integer | no |  | Sequential version within the `name` series, starting at `1`. |
| `description` | string \| null | no | default=None | Free-text description supplied at create time. |
| `runtime_sha256` | string | no |  | Hash identifying the integration runtime dependencies this build was produced against. |
| `src_code` | string | no |  | Python integration source code submitted for this build. |
| `requirements` | string | no | default='' | Pinned `pip` requirements submitted for this build. |
| `image` | string | no |  | Fully qualified Docker image reference for the built artifact. Absent if the build did not reach the publish step. |
| `base_image` | string \| null | no | default=None | Base image used for this build. Populated when the caller supplied `base_image`. |
| `program_language` | string | no | default='python3.10'; `OneOf` | Python runtime targeted by this build. One of `python2.7`, `python3.6`, `python3.10`. |
| `created_at` | number | no | range(min=0) | Build creation time (epoch seconds). |
| `created_by` | string | no |  | Email of the user who submitted the build. |
| `errors` | list[[IntegrationBuildErrorSchema](#schema-integrationbuilderrorschema)] \| null | no |  | Validation or build errors recorded for this build. Empty on success. |

### `LintFlake8RequestSchema` <a id='schema-lintflake8requestschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `src_code` | string | no |  | Python source to lint. |
| `cmd_args` | string | no |  | Additional whitespace-separated arguments to pass to `flake8`. |

### `LintFlake8ResponseSchema` <a id='schema-lintflake8responseschema'></a>

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `flake8_stdout` | string | no |  | Captured standard output from `flake8`. |
| `flake8_stderr` | string | no |  | Captured standard error from `flake8`. |
