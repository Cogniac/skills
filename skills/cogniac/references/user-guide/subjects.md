# Subjects

A subject is the central means by which concepts can be associated with media in the Cogniac system. Subjects also provide a mechanism by which media can be grouped and managed within the Cogniac system. Subjects can be simple concepts such as “cat” or more complex things such as “cat with mouse in mouth”. A subject can also be the “domain” of an image generation process, such as “cat door camera”, or any such logical grouping of related images.

| ****Name**** | ****Example**** | ****Description**** |
| --- | --- | --- |
| ****subject\_uid**** **string** | "cat\_1a" | **(read only)** Unique ID is automatically assigned to each Subject object upon creation. |
| ****name**** **string** | "Cat" | **(required)** Brief descriptive name of the subject. It can be multiple words. The maximum length of a subject name is 70 characters. |
| ****description**** **string** | "Domestic cats only." | **(optional)** Full description of the subject. Use this field to capture detailed subject semantics and feedback instructions. |
| ****expires\_in**** **float** | 1.0/31.0 | **(optional)** The time after which automatic subject-media expiration will take place. Accepts a floating point value in units of months. |
| ****external\_id**** **string** | "ABCcat123" | **(optional)** User-supplied id for the subject. |
| ****created\_at**** **float** | 1455044755 | **(read only)** Unix Timestamp |
| ****modified\_at**** **float** | 1455044770 | **(read only)** Unix Timestamp |
| ****created\_by**** **string** | "test@cogniac.co" | **(read only)** email of the user who created the subject |
| ****tenant\_id**** **string** | "lmulcvdfluyw" | **(read only)** tenant\_id of the user who created the subject |

Subject Media Expiration

The "expires\_in" time controls automatic subject-media expiration. It is specified in units of months. For this functionality, a month is defined to be 31 days. So, for example, to set an expiration time of 1 day, use an "expires\_in" value of 1/31 (approximately .03226).

The system periodically removes all subject-media associations older than the expiration time. This process never removes subject-media associations that have consensus. Note that the time of the last subject-media association update is used for expiration, so if a media item is processed or replayed multiple times, the most recent update would be used for expiration.

Please note that a media item will be deleted by the system when it is no longer associated with any subjects, e.g. after it expires from the last subject with which it was associated.
