# API Overview

## Overview

Cogniac has a full public API that exposes all of the system functionality. The Cogniac web applications are implemented using the Cogniac public API.

Our API uses resource-oriented URLs and HTTP response codes to describe API errors, and it works with any standard library such as cURL, urllib, etc. Most API requests require an access token you can generate using a valid user email and password combination.

## Basic API Structure

The API is comprised of:

1. ****Nodes**** - objects such as a User, Tenant, Application, or Detection
2. ****Edges**** - connections between nodes, such as a Tenant's Applications
3. ****Fields**** - information about Nodes, such as a Tenant's description or a User's email address

- An id in the API uniquely defines each Node

```
https://api.cogniac.io/1
```

- Where '1' is the API version you intend to use

```
GET https://api.cogniac.io/1/{node-id}
```

```
GET https://api.cogniac.io/1/{node-id}/{edge-name}
```

- All API requests must be made over HTTPS - API requests made over HTTP will fail.
- When using request libraries, the Cogniac API seamlessly accepts JSON parameters in the API requests. Depending on the request library, you may see errors if specifying the Content-Type header, so our guidance is to not use this header for JSON or media/files or requests. You can find the current API version by calling the /version endpoint.

```
GET https://api.cogniac.io/1/version
```

- The response will include the API version, build number, and build time.

```json
{
"version":"1",
"build_number":1055,
"build_time": "2016-12-14:06:08"
}
```

> ****Note:****
>
> You can also GET past API versions through a GET /1/version call, for example, which will return metadata for previous API versions.
