# Authentication

All Cogniac API calls, other than creating a user and retrieving a users's tenants, require a bearer access token to be included in the API request header.

An access token can be obtained through the `/1/token` endpoint. Users should include their valid username and password combination in the Basic authorization header of the `GET /token` request, along with the Tenant that they wish to log into, and the API will return the access token.

Each user in the Cogniac system can be a member of multiple Tenants, and to get access to a certain Tenant the user needs to use the token that was generated for that Tenant.

Example: Cogniac Authentication

## Step 1: Get List Of Tenants This User Can Access

To get the list of tenants a user has access to, a valid username and password must be passed to the `GET /1/users/{user_id}/tenants` endpoint.

"Current" Users and Tenants

For any User or Tenant endpoint in the Cogniac API, "current" can be substituted for a user ID or tenant ID. The given username and password, or bearer token, will be used to locate the correct user or tenant resource.

```
GET /1/users/current/tenants
Host: https://api.cogniac.io
```

### Example: Retrieving a User's Tenants

- [cURL](#tabs-2)
- [Python](#tabs-3)

```python
curl -X GET https://api.cogniac.io/1/users/current/tenants \
-u test@cogniac.co:password
```

```python
import requests
from requests.auth import HTTPBasicAuth

username = "test@cogniac.co"
password = "password"

# get the tenants this user has access to
resp = requests.get("https://api.cogniac.io/1/users/current/tenants",
                    auth=HTTPBasicAuth(username, password))
```

```
{
  "tenants": [
    {
      "tenant_id": "49wshskg",
      "type": "usertenant",
      "name": "Internal Tenant 1"
    },
    {
      "tenant_id": "12ir8sjgtl",
      "type": "orgtenant",
      "name": "External Tenant 2"
    }
  ]
}
```

## Step 2: Get Access Token For This User & The Specified Tenant

Once the user knows the Tenants they can access, they must request a token for a specific tenant with the `/token` endpoint as shown below.

```
GET /1/token
Host: https://api.cogniac.io
```

### Example: Retrieving an OAuth Token

- [cURL](#tabs-5)
- [Python](#tabs-6)

```curl
curl -X GET https://api.cogniac.io/1/token?tenant_id=12ir8sjgtl \
-u test@cogniac.co:password
```

```python
tenant_data = { "tenant_id" : "12ir8sjgtl" }
resp = requests.get("https://api.cogniac.io/1/oauth/token",
                    params=tenant_data,
                    auth=HTTPBasicAuth(username, password))
```

```
{
  "access_token": "abcdefghikjlmnop.qrstuvwxyzabcdefgh.ijklmnopqrs",
  "token_type": "Bearer",
  "expires_in": 432000,
  "user_email": "test@cogniac.co",
  "user_id": "38osksd",
  "tenant_id": "12ir8sjgtl",
  "tenant_name": "External Tenant 2",
  "tenant_type": "orgtenant"
}
```

After authenticating, users can make API requests with the following headers:

```
Authorization: Bearer abcdefghikjlmnop.qrstuvwxyzabcdefgh.ijklmnopqrs
```

## Step 3: Using the Access Token

### Example: Retrieving the Authenticated Tenant

- [cURL](#tabs-8)
- [Python](#tabs-9)

```curl
curl -X GET https://api.cogniac.io/1/tenants/current \
-H "Authorization: Bearer abcdefghikjlmnop.qrstuvwxyzabcdefgh.ijklmnopqrs"
```

```python
access_token = "abcdefghikjlmnop.qrstuvwxyzabcdefgh.ijklmnopqrs"
headers = {"Authorization":"Bearer %s" % access_token}
resp = requests.get("https://api.cogniac.io/1/tenants/12ir8sjgtl",
                    headers=headers)
```

```
{
  "tenant_id": "12ir8sjgtl",
  "type": "orgtenant",
  "name": "External Tenant 2",
  "created_at": 1234567890,
  "modified_at": 1234567890,
  "aws_region": "us-west-1",
  "created_by": "test@cogniac.co"
}
```
