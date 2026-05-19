# Tenants

A tenant is a siloed group of users sharing common applications and subjects. A typical tenant represents an organization or team where all users are trusted agents in providing feedback on subject media associations and application model detections.

For more information on the Cogniac data privacy model, see [Overview](/docs/cloudcore-overview).

## Tenant Fields

| ****Name**** | ****Example**** | ****Description**** |
| --- | --- | --- |
| ****tenant\_id**** **string** | "63QhzFLc9tg4" | **(read only)** Unique tenant\_id assigned to each Tenant object upon Tenant creation. |
| ****name**** **string** | "Cogniac Demo" | Brief name, usually including your company name |
| ****description**** **string** | "Example Cogniac Tenant" | More descriptive note about your Tenant/focus |
| ****aws\_region**** **string** | "us-west-1" | Amazon web services hosting region.    Currently, only "us-west-1" is supported and is added by default. |
| ****type**** **string** | "orgtenant" | Used to differentiate between a user's personal sandbox account and a group or company account to which others can be invited.    Possible values are 'orgtenant' and 'usertenant' |
| ****created\_at**** **float** | 1455044755 | **(read only)** Unix Timestamp |
| ****modified\_at**** **float** | 1455044770 | **(read only)** Unix Timestamp |
| ****created\_by**** **string** | "test@cogniac.co" | **(read only)** User email of account that created this Tenant |
