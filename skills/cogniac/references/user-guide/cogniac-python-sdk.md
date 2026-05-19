# Cogniac Python SDK

## Overview

The Python 2.7 SDK for the Cogniac Public API client library provides access to most of the common functionality of the Cogniac Public API. The package can be installed via "pip install cogniac" or via source from GitHub at <https://github.com/Cogniac/cogniac-sdk-py>.

The main entry point is the CogniacConnection object, which is created with the following credentials:

|  |  |
| --- | --- |
| ****username**** **string** | The Cogniac account username (usually an email address).    If the username is None, then use the contents of the COG\_USER environment variable as the username. |
| ****password**** **string** | The associated Cogniac account password.    If the password is None, then use the contents of the COG\_PASS environment variable as the username. |
| ****tenant\_id**** **string** | **(optional)**    Tenant ID with which to assume credentials.    This is only required if the user is a member of multiple tenants. If tenant\_id is None, and the user is a member of multiple tenants, then the contents of the COG\_TENANT environment variable will be used as the tenant\_id. |

```python
from cogniac import CogniacConnection

cc = CogniacConnection(username="test@cogniac.co",
                       password="myPassword",
                       tenant_id="63QhzFLc9tg4")
```

All Tenants

If a user is a member of multiple tenants, the user can retrieve a list of associated tenants via the `get_all_authorized_tenants` class method.

## CogniacConnection Class

- `CogniacConnection` gives a number of helper functions for working with common Cogniac objects such as applications, subjects, and media:
- `get_all_applications()`
  Return `CogniacApplications` for all applications belonging to the currently authenticated tenant.
- `get_application(app_id)`
  Return an existing `CogniacApplication`.
- `create_application(**app_kwargs)`
  Create a new `CogniacApplication`. Pass application configuration data as keyword arguments. For more information on application configuration fields, see [Applications](/docs/applications).
- `get_all_subjects()`
  Return `CogniacSubjects` for all subjects belonging to the currently authenticated tenant.
- `get_subject(subject_uid)`
  Return an existing `CogniacSubject`.
- `create_subject(**subject_kwargs)`
  Create a `CogniacSubject`. Pass subject configuration data as keyword arguments. For more information on subject configuration fields, see [Subjects](/docs/subjects).
- `get_media(media_id)`
  Return `CogniacMedia` object for an existing media item.
- `create_media(filename, **media_kwargs)`
  Create a new Cogniac media item from a given filename and media object keyword arguments. For more information on media configuration fields, see [Media](/docs/media).
- `get_tenant()`
  Return the currently authenticated `CogniacTenant`.
- CogniacApplication Class

  The `CogniacApplication` class is an object representing an Application in the Cogniac System. This class manages applications within the Cogniac System via the Cogniac public API application endpoints with the following methods:
- `create(CogniacConnection object, **app_kwargs)`
  Create a new application given an `CogniacConnection` instance and application configuration keyword arguments. Returns an `CogniacApplication` object.
- `get(CogniacConnection object, app_id)`
  Return an existing application, a `CogniacApplication` object.
- `get_all(CogniacConnection object)`
  Return all tenant's applications; returns a list of `CogniacApplication` objects.
- Writes to mutable CogniacApplication attributes are saved immediately via the Cogniac API.
- CogniacSubject Class

  The `CogniacSubject` class is an object representing a Subject in the Cogniac System. This class manages subjects within the Cogniac System via the Cogniac public API subject endpoints with the following methods:
- `create(CogniacConnection object, **subject_kwargs)`
  Create a new subject given an `CogniacConnection` instance and subject configuration keyword arguments. Returns an `CogniacSubject` object.
- `get(CogniacConnection object, subject_uid)`
  Return an existing subject object.
- `get_all(CogniacConnection object)`
  Return all subjects within the connected tenant.
- Writes to mutable `CogniacSubjects` attributes are saved immediately via the Cogniac API.
- CogniacMedia Class

  CogniacMedia objects contain metadata for media files that has been input into the Cogniac System. This class manages media within the Cogniac System via the Cogniac public API media endpoints with the following methods:
- `create(CogniacConnection object, filename, **media_kwargs)`
  Create a new media object given a `CogniacConnection` instance, image or video filename, and media configuration keyword arguments, return a `CogniacMedia` object.
- `get(media_id)`
  Returns an existing media object.
- CogniacTenant Class

  The `CogniacTenant` class is an object representing a Tenant in the Cogniac System. This class manages tenants within the Cogniac System via the Cogniac public API tenant endpoints.

```
import cogniac

cc = cogniac.CogniacConnection()  # COG_USER, COG_PASS, and COG_TENANT are set

print cc.get_tenant()

print cc.get_all_applications()

print cc.get_all_subjects()
```

Or to run iPython with extra magic commands:

```
% icogniac

print cc.tenant_id

%media_detections <media_id>

%media_subjects <media_id>
```
