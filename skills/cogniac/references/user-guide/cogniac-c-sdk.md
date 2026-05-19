# Cogniac C# SDK

.NET 4.6.1 C# SDK For Cogniac Public API

This client library provides access to most of the common functionality of the Cogniac public API. The main entry point is the Cogniac.Connection object.

The namespace Cogniac is used in this SDK, and all trivial types are nullable (E.G. long? ExpiresIn;).

## Class: Connection

|  |  |
| --- | --- |
| Description | Create an authenticated Cogniac connection with known credentials. |
| ****username**** **string** | **(optional)**    The Cogniac account username (usually an email address). If the username is not provided, then the contents of the COG\_USER environment variable is used as the username. |
| ****password**** **string** | **(optional)**    The associated Cogniac account password. If a password is not provided, then the contents of the COG\_PASS environment variable is used as the username. |
| ****tenantId**** **string** | **(optional)**    tenant\_id with which to assume credentials. This is only required if the user is a member of multiple tenants. If tenant\_id is not provided, and the user is a member of multiple tenant then the contents of the COG\_TENANT environment variable is used as the tenant id. |
| ****token**** **string** | **(optional)**   If a known API access token is provided, it can be used instead of all other parameters. (****This approach is recommended****). |
| ****urlPrefix**** **string** | **(optional)**    Do not use this parameter unless the API has been relocated to a different address. The default value is always used. |
| ****autoRenewToken**** **boolean** | **(optional)**    Allows the generated token to renew automatically once it expires mid-execution. The default value is true. |

The following methods are members of Cogniac.Connection object:

## GetAllAuthorizedTenants(username, password, urlPrefix)

|  |  |
| --- | --- |
| Description | Static method that returns an AuthorizedTenants object containing all tenants that a specific user is associated with. All the input parameters are used in the same manner as creating a Connection object. |
| Return | Cogniac.Tenants - multi-member object. |

****GetAuth()****

|  |  |
| --- | --- |
| Description | Returns an object containing the authentication information with the Cogniac API. |
| Return | Cogniac.Auth - multi-member object. |

****UploadMedia(forceSet, fileName, mediaTimestamp, forceOverwrite, metaTags, isPublic, externalMediaId, originalUrl, originalLandingUrl, license, authorProfileUrl, author, title, sourceUrl, previewUrl, localGatewayUrl)****

|  |  |
| --- | --- |
| Description | Uploads a media file to the Cogniac system. |
| ****forceSet**** **string** | **(optional)**    One of "training" or "validation", null otherwise. When it is null, it is random. |
| ****fileName**** **string** | **(optional)**    The full path and file name of media item to upload. If this is not provided, sourceUrl must be provided instead. |
| ****mediaTimestamp**** **long** | **(optional)**    User-specified image timestamp. |
| ****forceOverwrite**** **boolean** | **(optional)**    Overwrite any existing, identical media files and metadata. |
| ****metaTags**** **string array** | **(optional)**    Other associated metadata. |
| ****isPublic**** **boolean** | **(optional)**    Decides if the media is public or not, false if not provided. |
| ****externalMediaId**** **string** | **(optional)**    A unique ID for this media from it's external data source. |
| ****originalUrl**** **string** | **(optional)**    The original URL for this media. |
| ****originalLandingUrl**** **string** | **(optional)**    The original landing URL for this media. |
| ****license**** **string** | **(optional)**    License information about this media. |
| ****authorProfileUrl**** **string** | **(optional)**    Profile URL of the media owner. |
| ****title**** **string** | **(optional)**    Title of this media. |
| ****sourceUrl**** **string** | **(optional)**    Can pass an optional URL to the media to be created instead of a file. If not provided, fileName must be provided instead. |
| ****previewUrl**** **string** | **(optional)**    URL for media preview image for display. |
| ****localGatewayUrl**** **string** | **(optional)**    URL to upload media to, this is used when a local gateway is installed. |
| Return | Cogniac.Media - multi-member object. |

****DeleteMedia(mediaId, localGatewayUrl)****

|  |  |
| --- | --- |
| Description | Deletes a specific media file from the Cogniac system. |
| ****mediaId**** **string** | **(required)**    The media ID of the object to be deleted from the Cogniac system. |
| Return | Boolean - 'true' on success, 'false' otherwise. |

****GetAllSubjects(tenantId)****

|  |  |
| --- | --- |
| Description | Gets all subjects associated with a given tenant ID. |
| ****tenantId**** **string** | **(required)**    The tenant ID to pass to the API. |
| Return | Cogniac.Subjects - multi-member object. |

****GetSubject(subjectUid)****

|  |  |
| --- | --- |
| Description | Gets a subject associated with a given subject UID. |
| ****subjectUid**** **string** | **(required)**    The subject UID to pass to the API. |
| Return | Cogniac.Subject - multi-member object. |

****GetAllApplications(tenantId)****

|  |  |
| --- | --- |
| Description | Gets all applications associated with a given tenant ID. |
| ****tenantId**** **string** | **(required)**    The tenant ID to pass to the API. |
| Return | Cogniac.Applications - multi-member object. |

****GetApplication(applicationId)****

|  |  |
| --- | --- |
| Description | Gets an application associated with a given application ID. |
| ****applicationId**** **string** | **(required)**    The application ID to pass to the API. |
| Return | Cogniac.Application - multi-member object. |

****GetTenant(tenantId)****

|  |  |
| --- | --- |
| Description | Gets a tenant's information given a tenant ID. |
| ****tenantId**** **string** | **(required)**    The tenant ID to pass to the API. |
| Return | Cogniac.Tenant - multi-member object. |

****AssociateMediaToSubject(mediaId, subjectUid, forceFeedback)****

|  |  |
| --- | --- |
| Description | Associates an uploaded media to a given subject. |
| ****mediaId**** **string** | **(required)**    The unique ID of the media. |
| ****subjectUid**** **string** | **(required)**    The unique subject UID to associate the media with. |
| ****foreFeedback**** **boolean** | **(required)**    Forces the cogniac system to use the media for feedback. This value defaults to false if. |
| Return | Cogniac.Tenant - multi-member object. |

****GetMedia(mediaId)****

|  |  |
| --- | --- |
| Description | Gets a Cogniac.Media object from a given media ID. |
| ****mediaId**** **string** | **(required)**    The unique ID of the media. |
| Return | Cogniac.Media - multi-member object. |

****CreateSubject(name, description, publicRead, publicWrite)****

|  |  |
| --- | --- |
| Description | Create a subject in the Cogniac system. |
| ****name**** **string** | **(required)**    The name of the subject. |
| ****description**** **string** | **(optional)**    The description of the subject. |
| ****publicRead**** **boolean** | **(optional)**    Flag to select if the subject can be read publicly. |
| ****publicWrite**** **boolean** | **(optional)**    Flag to select if the subject can be written to publicly. |
| Return | Cogniac.Subject - multi-member object. |

****DeleteSubject(subjectUid)****

|  |  |
| --- | --- |
| Description | Deletes a subject from the Cogniac system. |
| ****subjectUid**** **string** | **(required)**    The unique ID of the subject to delete. |
| Return | Boolean - 'true' on success, 'false' otherwise. |

****CreateApplication(name, type, description, inputSubjects, outputSubjects, releaseMetrics, detectionThresholds, detectionPostUrls, gatewayPostUrls, active, requestedFeedbackPerHour, refreshFeedback, appManagers)****

|  |  |
| --- | --- |
| Description | Creates an application in the Cogniac system. |
| ****name**** **string** | **(required)**    Application name. |
| ****type**** **string** | **(required)**    Type of application (See API docs for valid types). |
| ****description**** **string** | **(optional)**    Application description. |
| ****inputSubjects**** **string array** | **(optional)**    List of input subjects to use. |
| ****outputSubjects**** **string array** | **(optional)**    List of output subjects to use. |
| ****releaseMetrics**** **string** | **(optional)**    Release metrics string. |
| ****detectionThresholds**** **dict** | **(optional)**    String dictionary of detection thresholds. |
| ****detectionPostUrls**** **string array** | **(optional)**    URL's where model detections will be surfaced in addition to web and iOS interfaces. |
| ****gatewayPostUrls**** **string array** | **(optional)**    A list of URL's where model detections will be surfaced from the gateway. |
| ****active**** **boolean** | **(optional)**    Controls if the the application is active or not. |
| ****requestedFeedbackPerHour**** **integer** | **(optional)**    Override the target rate of feedback to surface per hour. |
| ****refreshFeedback**** **boolean** | **(optional)**    Flag to control whether the images waiting for user feedback should be re-evaluated by the new model when a new model is released. |
| ****appManagers**** **string array** | **(optional)**    List of the application managers. |
| Return | Cogniac.Application - multi-member object. |

****GetSubjectMediaAssociations(subjectUid)****

|  |  |
| --- | --- |
| Description | Gets the subject media association given a subject UID. |
| ****subjectUid**** **subject** | **(required)**    The subject UID to pass to the API. |
| Return | Cogniac.SubjectMediaAssociations - multi-member object. |

****GetMediaSubjects(mediaId)****

|  |  |
| --- | --- |
| Description | Gets the subjects associated to a given media ID. |
| ****mediaId**** **string** | **(required)**    The unique ID of the media. |
| Return | Cogniac.MediaSubjects - multi-member object. |

For complete class definitions and detailed member descriptions, please visit: <https://github.com/Cogniac/cogniac-sdk-csharp>

SDK Usage Examples

All the examples assume: 'using Cogniac;'

Connecting to Cogniac with username, password, and tenant ID.

```
var cc = new Connection("someUser@company.com", "MyPassword", "ValidTenantID");
if (cc != null)
{
    var ao = cc.GetAuthObject();
    if (ao != null)
    {
        // Get the token for later use
        string token = ao.AccessToken;
    }
}
```

Connecting to Cogniac with a token.

```
string token = "ValidTokenSequence";
var cc = new Connection cc = new Connection(token: token);
if (cc != null)
{
    // The rest of the program
}
```

Connecting to Cogniac with a username and password but no tenant ID. (username is assumed to have 1 tenant)

```
var at = Connection.GetAllAuthorizedTenants("someUser@company.com", "MyPassword");
if (at != null)
{
    // Object 'at' will contain all the authorized tenants of this user, we use the first one
    var cc = new Connection("someUser@company.com", "MyPassword", at.Tenants[0].TenantId);
    var ao = cc.GetAuthObject();
    if (ao != null)
    {
        // Get the token for later use
        string token = ao.AccessToken;
    }
}
```

The following examples will assume a Cogniac.Connection object 'cc' has already been created properly.

Uploading a media item and associating it with a subject

```
string subjectUid = "KnownSubjectUid";
bool forceFeedback = true;
string[] tags = new string[] {"Media Owner", "BlackBerry KeyOne", "Android 7.1.1"};
string fullFileName = "Path\To\Image.jpg";
var m = cc.UploadMedia(fileName: fullFileName, metaTags: tags, forceOverwrite: true, isPublic: false);
if (m != null)
{
    var ci = _con.AssociateMediaToSubject(m.MediaId, subjectUid, forceFeedback);
    if (ci != null)
    {
        Console.WriteLine($"Association successful. CaptureId: '{ci.Id}'");
    }
}
```

Deleting a media item from the Cogniac system

```
string mediaId = "KnownMediaId";
if (cc.DeleteMedia(mediaId))
{
    Console.WriteLine("Media deleted");
}
else
{
    Console.WriteLine("Error deleting media");
}
```

Get subjects, subject, applications, application and tenant

```
string tenantId = "KnownTenantId";
string subjectUid = "KnownSubjectUid";
string appId = "KnownApplicationId";

var subjects = cc.GetAllSubjects(tenantId);
var subject cc.GetSubject(subjectUid);
var apps = cc.GetAllApplications(tenantId);
var app = cc.GetApplication(appId);
var t = cc.GetTenant(tenantId);
```

Create a Cogniac application

```
var app = cc.CreateApplication("TestApp", "classification");
if (app != null)
{
    // Application created properly, view it in JSON
    Console.WriteLine(Serialize.ToJson(app));
}
```

Create a Cogniac subject

```
var sub = cc.CreateSubject("test", "this is a test subject");
if (sub != null)
{
    // Subject created properly, view it in JSON
    Console.WriteLine(Serialize.ToJson(sub));
}
```

Get subject media associations

```
string subjectUid = "KnownSubjectUid";
var sma = cc.GetSubjectMediaAssociations(subjectUid);
```

Get media subjects

```
string mediaId = "KnownMediaId";
var ms = cc.GetMediaSubjects(mediaId);
```

## Utility: CogUpload.exe

Depends on all the "Release" DLLs output from the 'CogniacCSharpSDK' project.

```
Usage: CogUpload [-OPTION1 [ARG1]] [-OPTION2 [ARG1] [ARG2] [ARG3] ...] [-OPTION3 [ARG1]] ...

   * All options starts with '-' followed by a space after the option.
   * Arguments to each option follow the option directly.
   * If an option takes an array, the members are provided as space separated arguments.
   * All options take a single string argument unless specified.

List of available options:

-fs   | -ForceSet           Either 'training' or 'validation', don't provide it otherwise.
-f    | -FileName           Full path and file name of meida.
-d    | -Dirname            Directory of media files to process.
-u    | -Username           Cogniac issued username.
-p    | -Password           Cogniac issued password.
-tid  | -TenantId           Valid Cogniac tenant ID.
-tk   | -Token              Valid Cogniac access token.
-up   | -UrlPrefix          URL prefix of the Cogniac API.
-lgu  | -LocalGatewayUrl    Local gateway URL.
-mt   | -MediaTimestamp     Time stamp of the media.
-ff   | -ForceFeedback      ['True' or 'False' (default)] Force feedback after upload.
-fow  | -ForceOverwrite     ['True' (default) or 'False'] Force overwrite of media.
-mtg  | -MetaTags           [Array] List of meta tags of the media.
-isp  | -IsPublic           ['True' or 'False' (default)] Set media to public.
-emid | -ExternalMediaId    External media ID.
-ou   | -OriginalUrl        Original media URL.
-olu  | -OriginalLandingUrl Original landing URL.
-l    | -License            License link or text of the media.
-apu  | -AuthorProfileUrl   Author profile URL.
-t    | -Title              Title of the media.
-su   | -SourceUrl          Source URL of the media.
-pu   | -PreviewUrl         Preview URL of the media.
-suid | -SubjectUid         The Cogniac subject to associate the media with.
-r    | -Recursive          ['True' or 'False' (default)] Recursively upload files in 'DirName'.
-h    | -Help               Displays this help message.

   Note 1: 'TenantId' must always be provided unless 'Token' is used.
   Note 2: Either use 'Token' or 'Username' and 'Password' but not both. If both are provided 'Token'
       will be used and 'Username' and 'Password' will be ignored.
   Note 3: 'SubjectUid' must always be provided. It applies to all 'FileName' and/or 'DirName' uploads.
   Note 4: 'if 'DirName' is provided, all media within the directory will be uploaded recursively.
   Note 5: 'MediaTimestamp', 'ExternalMediaId', 'SourceUrl', 'OriginalUrl', 'OriginalLandingUrl',
       'Title', 'SourceUrl' and 'PreviewUrl' are single media file options only and cannot be
       applied to an entire directory. The rest of the options apply to every media file within
       the provided directory to process.
   Note 6: If both 'FileName and 'DirName' are provided, the single file will process first
       then the entire directory will process second.
   Note 7: Spaces in any string feild are NOT permitted, please use '+' instead.
       For example: '-f my image.png' is invalid, use '-f my+image.png' instead.
   Note 8: Options are NOT case-sensitive.

   Example 1:  CogUpload -f C:\Path\To\Image.png -u MYUSER -p MYPASSWORD -tid ABC123 -suid DEF456
   Example 2:  CogUpload -dirName C:\Path\To\Images -u MYUSER -p MYPASSWORD -tid ABC123 -suid DEF456
   Example 3:  CogUpload -fileName C:\Path\To\Image.png -token ABCDEF123456
           -mtg John+Doe BlackBerry Android+7.1.1 -IsPublic True -ff True -suid DEF456
```
