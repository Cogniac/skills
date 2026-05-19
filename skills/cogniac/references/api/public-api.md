# public-api

The `public-api` service exposes lightweight version probes for the Cogniac platform. It is intended as a deployment and connectivity check: callers can confirm that the service is reachable, identify the running build, and verify that a bearer token is accepted before exercising heavier endpoints. Both endpoints return a version string and are safe to poll.

## Endpoints

### `GET /1/version`

**return running version string**

Unauthenticated liveness probe. Returns the running service version.

**Auth:** no auth required

### `GET /1/authversion`

**return running version string**

Authenticated counterpart to `/1/version`. Returns the running service version once the caller's bearer token is validated; use it to verify that credentials are accepted end-to-end.

**Auth:** Bearer JWT required
