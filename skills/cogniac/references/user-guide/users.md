# Users

When first registered for a Cogniac account, a user account is automatically created. A user can be a member of multiple tenants with the same login credentials.

## User Fields

| ****Name**** | ****Example**** | ****Description**** |
| --- | --- | --- |
| ****user\_id**** **string** | "cJoiwcorTTm" | **(read only)** Unique user\_id assigned to each User object upon User creation. |
| ****given\_name**** **string** | "Jane" | First Name |
| ****surname**** **string** | "Smith" | Last Name |
| ****email**** **string** | "test@cogniac.co" | email address used for logging into the Cogniac system. |
| ****password**** **string** | "123ABCdef" | can be modified but not returned to the user with GET calls.   ****Password Requirements****  Minimum Password Length: 8  Maximum Password Length: 100  Minimum Number Of Required Lowercase Characters: 1  Minimum Number Of Required Numeric Characters: 1    Symbol and Diacritic characters are allowed, but not required. |
| ****tenant\_id**** **string** | "pipoyp63lqc7" | **(read only)** The ID of the tenant generated for the user. |
| ****tenant\_name**** **string** | "My Tenant" | **(read only)** The name of the tenant generated for the user. |
