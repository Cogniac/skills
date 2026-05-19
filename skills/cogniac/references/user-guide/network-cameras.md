# Network Cameras

A network camera is an RTSP or MJPEG streaming-enabled device optionally assigned to a gateway instance or the cloud infrastructure. A network camera is an object contained within a Network Camera application, allowing multiple network cameras to be grouped under a single network camera application.

| ****Name**** | ****Example**** | ****Description**** |
| --- | --- | --- |
| ****network\_camera\_id****  **string** | "9ehfiwhiu2" | **(read\_only)** Unique ID, used to identify the network camera. |
| ****url****  **string** | "rtsp://admin:password1@127.0.0.1" or  "http://19.168.10.76:81/mjpg/video.mjpg?COUNTER" | **(required)** Camera's Real Time Streaming Protocol (RTSP) URL. |
| ****active****  **boolean** | True | True = Camera is active - the camera will process frames. There is no direct control of the camera.      False = Camera is inactive - frames are not being processed from the camera. |
| ****camera\_name****  **string** | "Camera 1" | **(required)** user-specified camera name is included as a tag with all detections from this camera. |
| ****description****  **string** | "Security camera" | **(optional)** Additional user-provided description of the network camera. |
| ****latitude****  ****float**** | 37.3382 | **(optional)** latitudinal location of the camera |
| ****longitude****  ****float**** | 121.8863 | **(optional)** longitudinal location of the camera |
| ****hae****  ****float**** | 10 | **(optional)** expressed in meters. Reserved for UAV use. |
| ****created\_at****  **float** | 1463179215.124683 | **(read\_only)** Unix timestamp. |
| ****modified\_at****  **float** | 1463179215.124683 | **(read\_only)** Unix timestamp. |
| ****created\_by****  **string** | "admin-user@cognicac.co" | **(read\_only)** The user that created the network camera. |
| ****tenant\_id****  **string** | "rt06diepwc3i" | **(read\_only)** The tenant ID for the network camera |

## Create Network Camera

```
POST /1/networkCameras
Host: https://api.cogniac.io
```

```
{
  "url": "rtsp://admin:password1@127.0.0.1",
  "camera_name": "Camera 1",
  "description": "Cogniac Network Camera",
  "active": True,
  "longitude": -4.036878,
  "longitude": 39.669571
}
```

```
{
  "network_camera_id": "Asj45tQ1",
  "url": "rtsp://admin:password1@127.0.0.1",
  "camera_name": "Camera 1",
  "description": "Cogniac Network Camera",
  "active": True,
  "created_at": 1463179215.124683,
  "modified_at": 1463179215.124683,
  "tenant_id": "rt06diepwc3i",
  "created_by": "test@cogniac.co",
  "longitude": -4.036878,
  "longitude": 39.669571
 }
```

## Update Network Camera

The following endpoint is used to update a network camera's properties, e.g., URL or state.

```
POST /1/networkCameras/{network_camera_id}
Host: https://api.cogniac.io
```

The body of the request should contain a dictionary of the form:

```
{
  "description": "Cogniac Lobby Camera",
  "url": "rtsp://admin:password4@192.168.1.10:554/stream"
 }
```

```
{
  "network_camera_id": "Asj45tQ1",
  "url": "rtsp://admin:password4@192.168.1.10:554/stream",
  "camera_name": "Camera 1",
  "description": "Cogniac Lobby Camera",
  "active": True,
  "created_at": 1463179215.124683,
  "modified_at": 146318631.124683,
  "tenant_id": "rt06diepwc3i",
  "created_by": "test@cogniac.co"
 }
```

## Delete Network Camera

```
DELETE /1/networkCameras/{network_camera_id}
Host: https://api.cogniac.io
```

```
HTTP 204 Code (with no body)
```

Network Cameras Must Be Inactive Before Deletion

You must transition an application to 'inactive' before you can delete a Network Camera

## Enable/Disable network cameras associated with a gateway

```plaintext
POST /1/gateways/{gateway_id}/networkCameras
Host: https://api.cogniac.io
```

Input

```
{
    'network_camera_id' : [list of camera ids] OR 'all'
  'active' : True/False
}
```

Response

```
{
    'status':'success'
}
```
