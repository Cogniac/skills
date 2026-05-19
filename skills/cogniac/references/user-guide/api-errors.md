# API Errors

## The Cogniac API error response will send standard HTTP error codes by default.

In addition, the API uses descriptive error codes for each resource. These error codes are returned in the message body of HTTP errors, for example:

```
{"message": 'Invalid Input: Application not found. ## 0402002 ##'}
```

## Application Error Codes

| ****Code**** | ****Error**** |
| --- | --- |
| 0401000 | An invalid Subject ID was passed when attempting to create an application. |
| 0403001 | An invalid Subject ID was passed when attempting to update an application. |
| 0402002 | An incorrect Application ID was passed when attempting to retrieve an application. |
| 0403002 | An incorrect Application ID was passed when attempting to update an application. |
| 0404002 | An incorrect Application ID was passed when attempting to delete an application. |
| 0402005 | The user has attempted to retrieve applications belonging to a different tenant. |
| 0402006 | An incorrect Application ID was passed when attempting to retrieve an application model's CCP information. |
| 0402007 | No models were found when attempting to retrieve CCP information for the given Application ID. |
| 0402008 | Multiple models were found when attempting to retrieve CCP information for the given Application ID. |
| 0402009 | An incorrect Application ID was passed when attempting to retrieve an application model's CCP package. |
| 0402010 | The user has attempted to retrieve an application CCP package belonging to a different tenant. |
| 0402011 | An error occurred attempting to access an application CCP package stored in Amazon S3.    An uncommon occurrence, if the problem persists, contact user support. |
| 0403012 | No media files were found in the API request body when attempting to inject an image to be classified. |
| 0403013 | Multiple files were found in the API request body when attempting to inject an image to be classified.    Multiple image upload is currently not supported. |
| 0401016 | An invalid application type was passed when attempting to create an application. |
| 0401017 | An invalid model release metric was passed when attempting to create an application. |
| 0403018 | An application type was changed when attempting to update an application. Application types cannot be changed. |
| 0403019 | An invalid model release metric was passed when attempting to update an application. |
| 0401027 | A Subject ID not contained in the application's output\_subjects was passed in detection\_thresholds when creating an application. |
| 0403028 | A Subject ID not contained in the application's output\_subjects was passed in detection\_thresholds when updating an application. |
| 0401029 | An invalid probability value, a decimal between 0 and 1, was passed as a detection\_thresholds value when attempting to create an application. |
| 0403030 | An invalid probability value, a decimal between 0 and 1, was passed as a detection\_thresholds value when attempting to update an application. |
| 0403031 | A system timeout occurred while capturing existing media for detection. |
| 0404032 | Active applications cannot be deleted. Set the application to 'inactive' prior to deleting. |
| 0401033 | An empty string was passed as a detection\_post\_url when attempting to create an application. |
| 0403034 | An empty string was passed as a detection\_post\_url when attempting to update an application. |
| 0402035 | An invalid Application ID was passed when attempting to retrieve an application's pending detections. |
| 0403037 | A system timeout occurred while uploading new media for detection. |
| 0401039 | The user attempted to create a Twitter application with an invalid twitter\_queries map.   For information on Twitter queries, see ****Cogniac Applications**** |
| 0403040 | The user attempted to update a Twitter application with an invalid twitter\_queries map.   For information on Twitter queries, see ****Cogniac Applications**** |
| 0402042 | An invalid Application ID, or an application not within the authorized tenant, was passed when attempting to retrieve application feedback request messages. |
| 0403042 | An invalid Application ID, or an application not within the authorized tenant, was passed when attempting to post application feedback. |
| 0403047 | An application not within the authorized tenant, was passed when attempting to purge application feedback. |
| 0403048 | An error occurred while attempting to purge application feedback.    Application feedback can be purged only once every 60 seconds. |
| 0402049 | An invalid Application ID, or an application not within the authorized tenant, was passed when attempting to retrieve pending application feedback. |
| 0401050 | The user attempted to create a Twitter application with an invalid output subject. |
| 0401051 | The user attempted to create a Twitter application with a non-public output subject that belongs to a different tenant. |
| 0401052 | The user attempted to set an invalid requested\_feedback\_per\_hour while attempting to create an application.    Requested feedback must be a positive integer. |
| 0403053 | The user attempted to set an invalid requested\_feedback\_per\_hour while attempting to update an application.    Requested feedback must be a positive integer. |
| 0402054 | An invalid Application ID was passed when attempting to retrieve an application's replay status. |
| 0403054 | An invalid Application ID was passed when attempting to update an application's replay status. |
| 0403055 | The user attempted to updat a Twitter application with a non-public output subject that belongs to a different tenant. |
| 0402055 | An error occurred while attempting to send a replay message.    If the problem persists, contact user support. |
| 0401056 | The same Subject ID was used as input subject and output subject when attempting to create an application.    Input subjects cannot be output subjects within the same application or process of linked applications. |
| 0403057 | The same Subject UID was used as input subject and output subject when attempting to update an application.    Input subjects cannot be output subjects within the same application or process of linked applications. |
| 0401058 | When creating a Twitter application, output subjects should be passed in the 'twitter\_queries' custom field. |
| 0403059 | When updating a Twitter application, output subjects should be passed in the 'twitter\_queries' custom field. |
| 0401060 | More than the allowed maximum output subjects were provided when attempting to create an application.    Applications are limited to 1 to 20 output subjects depending on the application type. |
| 0403061 | More than the allowed maximum output subjects were provided when attempting to update an application.    Applications are limited to 1 to 20 output subjects depending on the application type. |
| 0402062 | An invalid Application ID was passed when attempting to retrieve an application's model release performance. |
| 0402063 | The client's system clock was out of sync with the server while attempting to query an application's model release performance.    In this case the duration field should be used instead. |
| 0402064 | A duration less than 0 was passed when attempting to access an application's model release performance. |
| 0402065 | An invalid Application ID was passed when attempting to retrieve an application's validation performance. |
| 0402066 | The client's system clock was out of sync with the server while attempting to query an application's validation performance.      In this case the duration field should be used instead. |
| 0402067 | A duration less than 0 was passed when attempting to access an application's validation performance. |
| 0402068 | An invalid Application ID was passed when attempting to retrieve an application's random test-set performance. |
| 0402069 | The client's system clock was out of sync with the server while attempting to query an application's random test-set performance.    In this case the duration field should be used instead. |
| 0402070 | A duration less than 0 was passed when attempting to access an application's random test-set performance. |
| 0403071 | One or more private subjects not belonging to the authorized tenant were passed when attempting to replay subject-media through an application.    Only the tenant's own or publicly readable subjects can be replayed. |
| 0402072 | An invalid Application ID was passed when attempting to retrieve an application's events. |
| 0402073 | An invalid Application ID was passed when attempting to retrieve an application's detections. |
| 0401074 | An empty string was passed as a gateway\_post\_url when attempting to create an application. |
| 0403075 | An empty string was passed as a gateway\_post\_url when attempting to update an application. |
| 0402076 | An invalid Application ID was passed when attempting to retrieve an application's subject-media consensus history. |
| 0403077 | Either a list of subject UID's or a media ID is required to replay media. |
| 0402078 | An invalid Application ID was passed when attempting to retrieve an application's model performance. |
| 0402079 | An application must have output subjects to retrieve model performance. |
| 0403080 | An inactive application cannot receive feedback. Ensure the application is set to active prior to providing feedback. |
| 0403081 | An invalid Application ID was passed when attempting to register for application event push notifications. |
| 0403082 | Application event push notifications can not be registered until push notifications are allowed on the current device. |
| 0401083 | A deprecated application type was passed when attempting to create a new application. |
| 0401084 | An empty string was passed as an application name when attempting to create a new application. |
| 0403085 | An empty string was passed as an application name when attempting to update an application. |
| 0403086 | A non-application manager attempted to update an application.    Only application managers can update applications. |
| 0404086 | A non-application manager attempted to delete an application.    Only application managers can delete applications. |
| 0403087 | An invalid Application ID was passed when attempting to purge application feedback. |
| 0403088 | The user attempted to remove all application managers while updating an application.    An application requires at least one application manager. |
| 0400100 | The user attempted to access resources for an application in a tenant they have no administrative rights in. |
| 0499999 | An unspecified error has occurred. |

## Subject Error Codes

| ****Code**** | ****Error**** |
| --- | --- |
| 0502000 | An incorrect Subject ID was passed when attempting to retrieve a subject. |
| 0503000 | An incorrect Subject ID was passed when attempting to update a subject. |
| 0504000 | An incorrect Subject ID was passed when attempting to delete a subject. |
| 0502001 | A valid Subject ID belonging to a different tenant was passed when attempting to retrieve a subject. |
| 0503001 | A valid Subject ID belonging to a different tenant was passed when attempting to update a subject. |
| 0504001 | A valid Subject ID belonging to a different tenant was passed when attempting to delete a subject. |
| 0504002 | subjects with either public\_read or public\_write set to True cannot be deleted. |
| 0502003 | An incorrect Subject ID was passed when attempting to retrieve subject media. |
| 0503003 | An incorrect Subject ID was passed when attempting to upload subject media. |
| 0504003 | An incorrect Subject ID was passed when attempting to delete subject media. |
| 0503004 | The user attempted to upload media to a private subject belonging to a different tenant. |
| 0504004 | The user attempted to delete media from a private subject belonging to a different tenant. |
| 0502005 | The user attempted to retrieve media from a private subject belonging to a different tenant. |
| 0502006 | An invalid result limit was passed when attempting to retrieve subject media.    Valid search limits are 1 to 1000. |
| 0502007 | One or more incorrect Subject ID's were passed when attempting to perform a batch ID search of subjects. |
| 0502008 | subject prefix search must include at least one tenant\_read\_write, public\_read, or public\_read\_write flag set to True. |
| 0502009 | subject similarity search must include at least one tenant\_read\_write, public\_read, or public\_read\_write flag set to True. |
| 0502010 | A negative duration value was passed when attempting to retrieving subject media. |
| 0502011 | A user attempted to query subject media however the client's system clock is out of sync with the server.    In this case the duration field should be used instead. |
| 0502012 | An incorrect Subject ID was passed when attempting to retrieve subject detections. |
| 0502013 | The user attempted to retrieve subject detections from a private subject belonging to a different tenant. |
| 0502014 | A probability\_upper value less than probability\_lower was passed when attempting to retrieve subject media. |
| 0504015 | subjects in use by applications cannot be deleted. Remove the subject from all applications before deleting. |
| 0503016 | subjects with either public\_read or public\_write set to True cannot be made private. |
| 0502017 | The user attempted to search subjects available to a different tenant.    Passing 'current' as the tenant\_id will return the subjects available to the authorized tenant. |
| 0503018 | When capturing media to a subject with consensus set to True or False, uncalibrated probability cannot be set. |
| 0502019 | An incorrect Subject ID was passed when attempting to retrieve subject consensus history. |
| 0502020 | The user attempted to retrieve subject consensus history from a private subject belonging to a different tenant. |
| 0599999 | An unspecified error occurred. |

## Media Error Codes

| ****Code**** | ****Error**** |
| --- | --- |
| 0201000 | No files were found in the request body when attempting to create new single-upload media. |
| 0201001 | Multiple files were found in the request body when attempting to create new single-upload media.    Multiple image upload is currently not supported. |
| 0201002 | An empty media file was found in the request body when attempting to create new single-upload media. |
| 0203004 | A meta-tags list longer than the allowed maximum was passed when attempting to update media.    Current media meta-tags limited to 32 items. |
| 0202005 | An incorrect Media ID was passed while attempting to retrieve media. |
| 0203005 | An incorrect Media ID was passed while attempting to update media. |
| 0204005 | An incorrect Media ID was passed while attempting to delete media. |
| 0201011 | A required field, **file\_size**, was missing when initiating resumable media upload. |
| 0201012 | Media was attempted to be uploaded using the resumable upload endpoint that exceeds the current maximum allowed file size.    Resumable media upload currently supports files less than or equal to 20GB. |
| 0201013 | A required field, **filename**, was missing when initiating resumable media upload. |
| 0201014 | A required field, **upload\_session\_id**, was missing when attempting to resume media upload.   **upload\_session\_id** and **video\_file\_chunk\_no** are required fields in order to successfully upload large media files. |
| 0201015 | A required field, **video\_file\_chunk\_no**, was missing when attempting to resume media upload.   **upload\_session\_id** and **video\_file\_chunk\_no** are required fields in order to successfully upload large media files. |
| 0201016 | An incorrect Session ID was passed when attempting to complete resumable media upload. |
| 0201017 | A file was found in the request body when attempting to initiate or complete resumable media upload. |
| 0201018 | Media was attempted to be uploaded using the resumable upload endpoint with a meta-tags list longer than the allowed maximum.    Current media meta-tags limited to 32 items. |
| 0201019 | A GIF file was found in the request body when attempting to create new single-upload media.    GIF files are not supported. |
| 0202023 | An existing media object was found when attempting to retrieve media, but belongs to a different tenant. |
| 0203023 | An existing media object was found when attempting to update media, but belongs to a different tenant. |
| 0204023 | An existing media object was found when attempting to delete media, but belongs to a different tenant. |
| 0201034 | A meta-tags list longer than the allowed maximum was passed when attempting to create new single-upload media.    Current media meta-tags limited to 32 items. |
| 0201035 | An existing media object was found when attempting to create resumable-upload media, but belongs to a different tenant. |
| 0201036 | A media object field contained an empty string when attempting to create single-upload media.    Empty strings are not allowable field entries. |
| 0203037 | A media object field contained an empty string when attempting to update media.    Empty strings are not allowable field entries. |
| 0203038 | A file was found in the request body when attempting to update existing media. |
| 0201039 | A timeout occurred awaiting a successful response while creating new single-upload media.    If the problem persists, contact support. |
| 0203040 | A timeout occurred awaiting a successful response while updating media.    If the problem persists, contact support. |
| 0204041 | User attempted to delete a media item that has been system-created from user-uploaded media.    System-derived media can only be deleted by removing the parent media. |
| 0202042 | An existing media object was found when attempting to retrieve media subjects, but belongs to a different tenant. |
| 0202043 | An incorrect Media ID was passed when attempting to retrieve media subjects. |
| 0202044 | An existing media object was found when attempting to retrieve media detections, but belongs to a different tenant. |
| 0202045 | An incorrect Media ID was passed when attempting to retrieve media detections. |
| 0201046 | Two identical media items to the file in the request body were found belonging to this tenant when attempting to create new single-upload media.    This is a rare error that can be corrected by contacting Cogniac support. |
| 0201048 | Two identical media items to the file in the request body were found belonging to this tenant when attempting to create new multi-part upload media.    This is a rare error that can be corrected by contacting Cogniac support. |
| 0201049 | An error occurred when attempting to access media from a source URL when creating new single-upload media.    Verify the given source URL is accessible. |
| 0201050 | An error occurred while attempting to complete a multi-part media upload.    Additional information specific to this error is contained in the the response body. |
| 0201051 | An AVI file was found in the request body when attempting to create new single-upload media.    AVI files are not supported. |
| 0202052 | More than one media item was found when searching for media by MD5 within the given tenant.    This is a rare error that can be corrected by contacting Cogniac support. |
| 0202053 | An incorrect MD5 hash string was passed when attempting to retrieve media by it's MD5. |
| 0299999 | An unspecified error occurred. |

## Gateway Error Codes

| ****Code**** | ****Error**** |
| --- | --- |
| 0801000 | A name is required to create a Gateway. |
| 0801005 | A gateway with that Gateway ID already exists in this tenant. |
| 0801006 | A gateway local\_post\_interval must be a number greater than 0. |
| 0802011 | An incorrect Gateway ID was passed when attempting to retrieve a gateway. |
| 0803011 | An incorrect Gateway ID was passed when attempting to update a gateway. |
| 0804011 | An incorrect Gateway ID was passed when attempting to delete a gateway. |
| 0803012 | A gateway local\_post\_interval must be a number greater than 0. |
| 0802018 | An incorrect Gateway ID was passed when attempting to retrieve gateway status. |
| 0803018 | An incorrect Gateway ID was passed when attempting to delete gateway status. |
| 0899999 | An unspecified error occurred. |

## Network Camera Error Codes

|  |  |
| --- | --- |
| 0901000 | A valid RTSP url of the type 'rtsp://..' is required to create a Network Camera. |
| 0901001 | A name is required to create a Network Camera. |
| 0902002 | An incorrect Network Camera ID was passed when attempting to retrieve a network camera. |
| 0903002 | An incorrect Network Camera ID was passed when attempting to update a network camera. |
| 0904002 | An incorrect Network Camera ID was passed when attempting to delete a network camera. |
| 0902003 | The user has attempted to access the network cameras belonging to a different tenant. |
| 0999999 | An unspecified error occurred. |

## Tenant Error Codes

| ****Code**** | ****Error**** |
| --- | --- |
| 0004006 | A tenant can not be deleted if there are existing applications, subjects, or gateways within that tenant.    Delete all applications, subjects, and gateways to successfully delete a tenant. |
| 0004008 | No group membership for this user was found when trying to remove a user from the tenant. |
| 0001009 | A user or tenant could not be found when attempting to add a user to a tenant. |
| 0099999 | An unspecified error occurred. |

## User Error Codes

| ****Code**** | ****Error**** |
| --- | --- |
| 0102000 | An incorrect User ID was passed when attempting to retrieve a user. |
| 0103001 | A user has attempted to update a user not within their scope.    Only administrators may access other users. |
| 0104001 | A user has attempted to delete a user not within their scope.    Only administrators may delete other users. |
| 0100006 | An invalid username or password was provided while attempting to retrieve an authorization token. |
| 0100011 | An incorrect tenant ID was passed when attempting to retrieve an authorization token. |
| 0104012 | The authorized user does not have privileges to delete the given User ID. |
| 0101013 | An error occurred while creating a user or group account.    Additional error information is contained in the 'details' entry of the response body. |
| 0100016 | Either a tenant\_id or scope = all must be passed when attempting to retrieve an authorization token. |
| 0100017 | Either a valid token or password were not passed when attempting to update a password.    A valid password reset token and new password are required. |
| 0100018 | An invalid password reset token was passed when attempting to update a password.    A valid password reset token and new password are required. |
| 0100019 | An error occurred when attempting to update a password. Specific error details are included in the error message. |
| 0100020 | An error occurred when sending an account verification email. Specific error details are included in the error message. |
| 0100021 | An error occurred when sending a password reset email. Specific error details are included in the error message. |
| 0102024 | No memberships were found for the given user when attempting to retrieve a user's tenants. |
| 0101025 | The user attempted to register a device for push notifications without a valid device token. |
| 0101026 | A user with a matching email address was found when attempting to create a new user. |
| 0199999 | An unspecified error occurred. |

## Invite Error Codes

| ****Code**** | ****Error**** |
| --- | --- |
| 1103005 | An invalid user ID or email was passed when attempting to update a user invite. |
| 1103006 | A user invite can only be updated if it is in the "pending" state. |
| 1103007 | Invitation status is a required field to update a user invite.    Accepted values are "accepted" or "declined". |
| 1103008 | An invalid tenant ID or role were given when attempting to accept a user invitation. |
| 1103009 | An error occurred while sending a user invite email.    If the problem persists, contact Cogniac support. |
| 1103010 | An error occurred while attempting to delete a user invite. |
| 1199999 | An unspecified error occurred. |
