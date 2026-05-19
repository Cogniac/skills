# Cogniac CLI Tool

## Overview

The Cogniac CLI (`cogniac`) is an agent-friendly command-line interface for the Cogniac Public API. It outputs JSON by default or formatted tables for human-readable output. The CLI is included with the Cogniac Python SDK and can be installed via `pip install cogniac` or via source from GitHub at <https://github.com/Cogniac/cogniac-sdk-py>.

## Authentication

The CLI authenticates using environment variables:

|  |  |
| --- | --- |
| ****COG\_USER**** **string** | The Cogniac account username (usually an email address). |
| ****COG\_PASS**** **string** | The associated Cogniac account password. |
| ****COG\_API\_KEY**** **string** | **(optional)** A Cogniac-issued API key (alternative to username/password). |
| ****COG\_TENANT**** **string** | **(optional)** Tenant ID with which to assume credentials. Only required if the user is a member of multiple tenants. |
| ****COG\_URL\_PREFIX**** **string** | **(optional)** Cogniac API endpoint URL. Defaults to `https://api.cogniac.io/`. |

```bash
export COG_USER="user@example.com"
export COG_PASS="yourpassword"
export COG_TENANT="your_tenant_id"

cogniac auth
```

## Global Options

|  |  |
| --- | --- |
| ****--format json**** | Output as JSON (default). Ideal for scripting and automation. |
| ****--format table**** | Output as a formatted table for human-readable display. |

```bash
cogniac apps list --format table
```

## Commands

### Auth and Tenant

- `cogniac auth`
  Check credentials and connectivity. Returns auth method, tenant info, and validity status.
- `cogniac user`
  Show current user info including system roles.
- `cogniac tenant`
  Show current tenant info including tenant\_id, name, description, and region.
- `cogniac tenants`
  List all authorized tenants. Does not require COG\_TENANT to be set.
- `cogniac version`
  Show API version info.

### Applications

- `cogniac apps list`
  List all applications belonging to the currently authenticated tenant.
- `cogniac apps get <application_id>`
  Get details for a specific application.

### Subjects

- `cogniac subjects list`
  List all subjects belonging to the currently authenticated tenant.
- `cogniac subjects get <subject_uid>`
  Get a specific subject.
- `cogniac subjects search [--prefix P] [--name N] [--similar S] [--ids ID ...] [--limit L]`
  Search subjects with filters. `--prefix` filters by name prefix, `--similar` finds semantically similar subjects, `--name` matches exact name, `--ids` retrieves specific UIDs, `--limit` sets max results (default: 10).
- `cogniac subjects media <subject_uid> [--limit L] [--consensus C] [--probability-lower P] [--probability-upper P]`
  List media associations for a subject. `--consensus` filters by `True`, `False`, or `Sidelined`.
- `cogniac subjects create <name> [--description D] [--external-id E]`
  Create a new subject with the given name. Optionally provide a description and external identifier.
- `cogniac subjects associate <subject_uid> <media_id> [--consensus C]`
  Associate media with a subject. `--consensus` sets the label: `True`, `False`, `Sidelined`, or `None` (default: `None`).

```bash
cogniac subjects search --prefix "defect" --limit 20 --format table

cogniac subjects create "My Subject" --description "Defect detection subject"

cogniac subjects associate "subject_uid_here" "media_id_here" --consensus True
```

### Media

- `cogniac media get <media_id>`
  Get a specific media item.
- `cogniac media search [--md5 M] [--filename F] [--external-media-id E] [--domain-unit D] [--limit L]`
  Search media with filters.
- `cogniac media upload <filename> [--subject-uid S] [--external-media-id E] [--domain-unit D] [--meta-tags T ...]`
  Upload a media file. If `--subject-uid` is provided, the media is automatically associated with that subject after upload.

```bash
cogniac media search --filename "image001.jpg"

cogniac media upload /path/to/image.jpg --subject-uid "subject_uid_here"
```

### EdgeFlows

- `cogniac edgeflows list`
  List all EdgeFlow devices.
- `cogniac edgeflows get <edgeflow_id>`
  Get a specific EdgeFlow.
- `cogniac edgeflows status <edgeflow_id> [--subsystem S] [--limit L]`
  Get EdgeFlow status events. `--subsystem` filters by subsystem name (e.g. `model_detections`, `ifconfig`, `ping`). `--limit` sets max results (default: 10).

```bash
cogniac edgeflows status "gateway_id_here" --subsystem model_detections --limit 5
```

### Cameras

- `cogniac cameras list`
  List all network cameras.
- `cogniac cameras get <network_camera_id>`
  Get a specific camera.

### Deployments and Workflows

- `cogniac deployments list`
  List all deployment groups.
- `cogniac deployments get <deployment_group_id>`
  Get a specific deployment group.
- `cogniac workflows get <workflow_id>`
  Get a specific workflow.

## Error Handling

The CLI outputs errors as JSON to stderr with an `error` type and `detail` message:

|  |  |
| --- | --- |
| ****CredentialError**** | Invalid credentials (HTTP 401). Check your COG\_USER/COG\_PASS or COG\_API\_KEY. |
| ****ClientError**** | Client-side error (HTTP 4xx). Typically a bad request or resource not found. |
| ****ServerError**** | Server-side error (HTTP 5xx). The CLI will retry automatically with exponential backoff. |
| ****AuthError**** | No credentials configured. Set the required environment variables. |

## Additional CLI Tools

The Cogniac Python SDK includes three additional command-line utilities:

### icogniac — Interactive Shell

An IPython shell with pre-loaded Cogniac magic commands and automatic authentication. Provides a `CogniacConnection` object (`cc`) ready to use.

```
% icogniac

print cc.tenant_id

%media_detections <media_id>

%media_subjects <media_id>
```

### cogupload — Parallel Media Upload

Robust parallel upload of media files to a Cogniac subject using 24 threads with automatic retry on server errors.

Supported file types:
- BMP
- JPG / JPEG
- PNG
- AVI
- MP4
- MOV

|  |  |
| --- | --- |
| ****subject\_uid**** **string** | The target subject UID for media association. |
| ****directory**** **string** | Directory containing media files to upload. |
| ****-r**** | **(optional)** Recursively upload all media files under the directory. |

```bash
cogupload "subject_uid_here" /path/to/images/

cogupload "subject_uid_here" /path/to/images/ -r
```

### cogstats — EdgeFlow Statistics

Aggregates EdgeFlow device statistics including model detections, media pixel counts, and GPU pixel counts.

|  |  |
| --- | --- |
| ****-t, --tenant\_id**** **string** | **(required)** Tenant ID. |
| ****-g, --gateway\_id**** **string** | **(optional)** Filter to a specific EdgeFlow device. |
| ****-s, --start\_timestamp**** **float** | **(optional)** Start time (Unix timestamp). |
| ****-e, --end\_timestamp**** **float** | **(optional)** End time (Unix timestamp). |

```bash
cogstats -t "your_tenant_id"

cogstats -t "your_tenant_id" -g "gateway_id" -s 1700000000 -e 1700100000
```
