# Cogniac - Users

Return specified tenant's users, sorted from A-> Z (based on the first name of Users)

## Tenant's Users

| ****Argument**** | ****Description**** |
| --- | --- |
| ****tenant\_id**** **boolean** | **(required)** The unique identifier of the Tenant object to be retrieved |
| ****reverse**** **boolean** | **(optional)** Results order can be reversed by adding the ?reverse=true parameter |

```
GET /1/tenants/{tenant_id}/users
Host: https://api.cogniac.io
```

## Example: List Tenant's Users

- [cURL](#tabs-2)
- [Python](#tabs-3)

```curl
curl -X GET https://api.cogniac.io/1/tenants/current/users \
-H "Authorization: Bearer abcdefg.hijklmnop.qrstuvwxyz" \
| json_pp
```

```python
import requests
import json
from pprint import pprint

url_prefix = 'https://api.cogniac.io'
api_version = "1"
token = ''  # add your token here
headers = {'Authorization': f'Bearer {token}'}

url = f'{url_prefix}/{api_version}/tenants/current/users'
res = requests.get(url, headers=headers)

if res.status_code == 200:
    response_data = json.loads(res.content)
    pprint(response_data)
else:
    print(f"Error: {res.status_code}, {res.text},{res.headers}")
```

```
{
  "data": [
    {
       "tenant_id": "qqkbbkqvio08",
       "name": "Jane Smith",
       "user_id": "2ke2daisdflkj",
       "given_name":"Jane",
       "surname":"Smith",
       "username":"test@cogniac.co",
       "created_by": "test@cogniac.co"
    },
        {
            //Next User Object ...
    }
    ]
}
```

Remove User From Tenant

This endpoint will remove a user from a tenant but not delete a user's account.

To remove a user from a tenant, the following arguments should be passed:

| ****Argument**** | ****Description**** |
| --- | --- |
| ****user\_id**** **string** | **(required)** ID of the user to remove from the tenant. |

```plaintext
DELETE /1/tenants/{tenant_id}/users?user_id=fladkjhflkdaj
Host: https://api.cogniac.io
```

Example: Remove a User from a Tenant

- [cURL](#tabs-5)
- [Python](#tabs-6)

```curl
curl -X DELETE https://api.cogniac.io/1/tenants/current/users?user_id=0Wd765esrdtyuijkn \
-H "Authorization: Bearer abcdefg.hijklmnop.qrstuvwxyz" \
| json_pp
```

```python
import requests
from pprint import pprint

url_prefix = 'https://api.cogniac.io'
api_version = "1"
token = ''  # add your token here
headers = {'Authorization': f'Bearer {token}',
           'Content-Type': 'application/json'}
user_data = {
    "user_id": "QTavhd110T0BBan8Zgoalm"
  }

url = f'{url_prefix}/{api_version}/tenants/current/users'
res = requests.delete(url, json=user_data, headers=headers)
print(res)
if res.status_code == 204:
    print(f"{user_data} was successfully deleted. ")
else:
    pprint(f"Error: {res.status_code}, {res.text},{res.headers}")
```

```
<Response [204]>
{user_id": "QTavhd110T0BBan8Zgoalm} was successfully deleted.
```

Tenant User roles

A user can belong to any of the three roles below

- Tenant Admin
- Tenant User
- Tenant Viewer

| Role | User management | App Management | Feedback | Read/Write access to tenant data | Edge & Cloud Flow operations | Operations Review & External Inspection |
| --- | --- | --- | --- | --- | --- | --- |
|  | Create new users, delete, change permissions, invite users, change name, and description. | Add new subjects and change app name, description, type, and detection thresholds. | Provide feedback | Media, apps, feedback, subjects, cameras | Create gateways, deployment groups, & trigger camera capture |  |
| Tenant Admin | Yes | Yes | Yes | Yes | Yes | Yes |
| Tenant User | No | Only if App Manager | Yes | Yes | Yes | Yes |
| Tenant Operator | No | Only if App Manager | Yes | Yes | No | Yes |
| Tenant Viewer | No | No | No | Read-only access | No | No |
| Tenant Billing | No | No | No | Read-only access | No | Yes |
| Annotator | No | No | Yes | Read-only access | No | No |
| Expert Annotator | No | No | Yes | Read-only access | No | No |

### Annotator and Expert Annotator

Users with either the Annotator or Expert Annotator roles are limited to providing feedback and viewing a tenant's state. They do not have permission to create, delete, or modify any resources within the tenant. The permissions for both roles are identical, with no differences in their capabilities or the resulting behavior when feedback is provided.
