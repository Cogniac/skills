# CloudCore Management of Edgeflows

An EdgeFlow performs GPU-accelerated inference for on-premises data sources, e.g., network cameras located on a production line can directly communicate with an EdgeFlow for near real-time inference. The EdgeFlow can communicate with Cogniac cloud infrastructure for downloading models, uploading statistics, and selecting images for feedback.

Every EdgeFlow object has the following fields.

| ****Name**** | ****Example**** | ****Description**** |
| --- | --- | --- |
| ****gateway\_id**** **string** | "Ajr2t45p" | A unique ID used to identify the EdgeFlow. |
| ****name**** **string** | "Headquarters office gateway" | EdgeFlow name, should be brief and descriptive. |
| ****description**** **string** | "Security cameras gateway" | EdgeFlow description should be a brief yet complete description of the focus of this gateway. |
| ****location**** **string** | "cogniac-hq" | Location of the EdgeFlow. |
| ****poll\_interval**** **integer** | 20 | The interval at which updates to the EdgeFlow configuration are implemented in the system in seconds.    It defaults to 20 seconds.    Accepts values greater than or equal to 1 second. |
| ****model**** ****string**** | EdgeFlow-RM-M20 | The EdgeFlow's device model. |
| ****mac\_address**** **string** | "01-23-45-67-89-ab" | The media access control (MAC) address of the gateway device. The MAC address is obtained from the first Ethernet device discovered on the EdgeFlow. The value is immutable. |
| ****serial\_number**** **string** | "1234567-890-aabb" | The serial number of the EdgeFlow device. |
| ****ip\_address**** **string** | "123.45.67.89" | The IP of the gateway device. Assigned based on the IP address of the requesting device during EdgeFlow creation. |
| ****Model Deployment Policy**** ****string**** | "latest" | This field is used to control which models the EdgeFlow uses for inference. There are 3 options:  "latest" - use current best model, "production" - use production models specified in app configuration, or "staging" - use staging models as specified in-app configuration.  The default is "latest". |
| ****created\_at**** **float** | 1463179215.124683 | Unix timestamp. |
| ****modified\_at**** **float** | 1463179215.124683 | Unix timestamp. |
| ****created\_by**** **string** | "admin-user@cognicac.co" | The user that created the EdgeFlow. |
| ****tenant\_id**** **string** | "rt06diepwc3i" | The tenant ID for the EdgeFlow**.** |
| ****input subjects**** **string** | "input\_subject\_1" | A list of input subjects that can be used to invoke /1/process/<input\_subject\_uid> calls to the local inference API.  If the input subject is not specified, the /1/process/<input\_subject\_uid> api will return a 404 - subject not found error. |

There are additional fields when querying the status of a Gateway. They are listed on [Gateways - Status](/docs/gateways-status) page.
