# Media

Media corresponds to still images or video. Media can be either uploaded into the Cogniac System manually by authenticated users or the system can actively acquire media from external sources such as network cameras.

| ****Name**** | ****Example**** | ****Description**** |
| --- | --- | --- |
| ****media\_id**** **string** | "media\_id\_123" | **(required)** Unique media\_id is automatically assigned to each Media object upon creation |
| ****tenant\_id**** **string** | iut6rfcgbn | **(required)** ID of the tenant that owns this unique media object. |
| ****uploaded\_by\_user**** **string** | "test@cogniac.co" | **(read\_only)** Username of the user that uploaded media. |
| ****created\_at**** **float** | 1455044755 | **(read\_only)** Original upload timestamp of the media. |
| ****status**** **string** | "success" | **(read only)** One of "success" or "failed"; represents whether or not the media data upload was successful.  If "failed", there was an issue saving the media file. Try uploading again. If the problem persists, contact Cogniac support. |
| ****media\_fomat**** **string** | "jpg" | **(read only)** File format of the media. |
| ****image\_width**** **integer** | 227 | **(read only)** The width of the media file, in pixels.  Determined by the Cogniac system. |
| ****image\_height**** **integer** | 227 | **(read only)** The height of the media file in pixels.  Determined by the Cogniac system. |
| ****size**** **float** | 4096 | **(read only)** The size of the media file in bytes. |
| ****md5**** **string** | "901565ac32dab9b3cc1e356441a10ed7" | **(read only)** the MD5 hash of the media file. |
| ****parent\_media\_id**** **string** | "Ah34RTqn9s56fGTY" | **(read only)** Cogniac ID of the parent media to this item.  E.g., the ID of a video file in which a media object is a single frame. |
| ****parent\_media\_ids**** **array** | ['1eedcf600c7edc0661354dd1f9a60eb9', '20b6e4aff0eab77fea32261e9fb355f4'] | **(read only)** Array of parent media\_ids from which the media was derived.  parent\_media\_ids[0] will always be the original media\_id uploaded to Cogniac.  parent\_media\_ids[-1] will always be the parent\_media\_id. |
| ****frame**** **integer** | 20 | **(read only)** The frame number of this media item in its parent video media. Frame count starts at 0.  **(For video child media only.)** |
| ****fps**** **float** | 24 | **(read only)** Frames-per-second.  **(For video media only.)** |
| ****time\_base**** **integer** | 20 | **(read only)** The reference clock frequency used by a camera to timestamp frames. Measured in KHz.  **(For video media only.)** |
| ****frame\_durations**** **array** | [1205, 1238, 1252, 1199, ...] | **(read only)** A list of frame durations. Measured in 10's of microseconds.  **(For video media only.)** |
| ****num\_frames**** **integer** | 500 | **(read only)** The number of frames in video media.  **(For video media only.)** |
| ****duration**** **float** | 600 | **(read only)** Duration of the video media.  **(For video media only.)** |
| ****video**** **bool** | True | **(read only)** True - video media False - image media |
| ****set\_assignment**** **string** | "validation" | **(read only)** One of "training" or "validation". Denotes whether the media will be used as training or validation data for model development. |
| ****media\_url**** **string** |  | **(read only)** A download url to access the original media item. |
| ****resize\_urls**** **map** |  | **(read only)** A map, indexed by size (in pixels), of resized versions of the original media data.  Media items are automatically stored with resized thumbnails. Thumbnails are only created by down-sizing media. Any media item that is already smaller than the smallest supported thumbnail size will not be resized to be larger. |
| ****media\_timestamp**** **float** | 1234567890 | **(optional)** User-specified image timestamp, usually it is the time when the image is physically created |
| ****media\_src**** **string** | "Twitter" | **(optional)** Origin of this media, such as google, facebook, flickr, etc, command\_line, |
| ****filename**** **string** | "my\_image.jpg" | **(optional)** Filename of the uploaded media. |
| ****meta\_tags**** **array** | "meta\_tags": [  "test@cogniac.co" ], | **(optional)** Other associated metadata. |
| ****external\_media\_id**** **string** | "000060e3121c7305" | **(optional)** A unique ID for this media from it's external data source.  E.g., the ImageID field from the OpenImages dataset. |
| ****domain\_unit**** **string** | "part\_123" | **(optional)** domain id (e.g. serial number) for set assignment grouping.  Media with the same domain\_unit will always be assigned to the same training or validation set. Set this to avoid overfitting when you have multiple images of the same thing or almost the same thing. |
| ****network\_camera\_id**** **string** | "97654rtyh" | **(optional)** ID of the [Cogniac Network Camera](https://cogniac.readme.io/docs/network-cameras) that captured the media. |
| ****original\_url**** **string** | "<https://c1.staticflickr.com/5/4129/5215831864_46f356962f_o.jpg>" | **(optional)** The original URL for this media.  E.g., the OriginalURL field from the OpenImages dataset. |
| ****original\_landing\_url**** **string** | "<https://www.flickr.com/photos/brokentaco/5215831864>" | **(optional)** The original landing URL for this media.  E.g., the OriginalLandingURL field from the OpenImages dataset. |
| ****license**** **string** | "<https://creativecommons.org/licenses/by/2.0/>" | **(optional)** License information about this media.  E.g., the URL in the License field of the OpenImages dataset. |
| ****author\_profile\_url**** **string** | "<https://www.flickr.com/people/brokentaco/>" | **(optional)** URL of the media owner.  E.g., the AuthorProfileURL field from the OpenImages dataset. |
| ****author**** **string** | "David" | **(optional)** Name of the media owner.  E.g., the Author field from the OpenImages dataset. |
| ****title**** **string** | "28 Nov 2010 Our new house." | **(optional)** Title of this media.  E.g., the Title field from the OpenImages dataset. |
| ****source\_url**** **string** | "<https://c1.staticflickr.com/5/4129/5215831864_46f356962f_o.jpg>" | **(optional)**  Can pass an optional URL to the media to be created instead of a file. |
| ****preview\_url**** **string** | "<https://c1.staticflickr.com/5/4129/5215831864_46f356962f_o.jpg>" | **(optional)**  URL for media preview image for display. |
