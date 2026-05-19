# Meraki API Advanced Setup Guide

## 1. Introduction

This quick start guide outlines the steps required to integrate a Cogniac CloudCore™ tenant with a Meraki Cloud. This process requires a CloudCore™ tenant with an enabled Meraki feature set and a Meraki account. The following Meraki MV camera models are currently supported: MV2, MV12, MV22, MV32, MV72, MV63 and MV93.

![](../../../assets/media/images/meraki-api-advanced-setup-guide-2023-image-4tvwu553.png)

## 2. Configure Meraki Dashboard for API Access

Please refer to the Cisco Meraki Dashboard API documentation for steps to enable API access and generate a Meraki dashboard API key: <https://documentation.meraki.com/General_Administration/Other_Topics/Cisco_Meraki_Dashboard_API>

## 3. Configure Meraki Dashboard API Key in Cogniac CloudCore™

3.1 Go to the CloudCore™ tenant Settings configuration page:

![](../../../assets/media/images/meraki-api-advanced-setup-guide-2023-image-hsq5rpik.png)

3.2 Scroll down to the Integrations section:

If the tenant settings page does not have an Integrations section with Meraki configuration items, as shown above, your tenant is not configured with the Meraki integrations feature set. Please contact your Cogniac account team for assistance.

![](../../../assets/media/images/meraki-api-advanced-setup-guide-2023-image-dts1s6up.png)

Input the Meraki Dashboard API Key. The organization ID will automatically populate if your API key has access to a single Meraki organization. If your API key has access to multiple Meraki organizations, you must select the organization you would like to access from the CloudCore™ tenant.

![](../../../assets/media/images/meraki-api-advanced-setup-guide-2023-image-hs8qtz7j.png)

## 4. Create a Meraki Camera Capture Application in CloudCore™

A CloudCore Meraki Camera Capture application allows you to capture periodic snapshots from your Meraki cameras directly into CloudCore™ via the Meraki API camera snapshot interface. To do this, create a new Meraki Camera Capture app and configure it with the cameras you want to use for image capture purposes.

4.1 Select the Meraki Camera capture application type and provide a name for the new application. ![](../../../assets/media/images/meraki-api-advanced-setup-guide-2023-image-q5f5gg2u.png)

4.2 Select individual cameras that you would like to use from a list of cameras that are present in your Meraki organization.

![](../../../assets/media/images/meraki-api-advanced-setup-guide-2023-image-zyiq9c39.png)

4.3 Optionally, modify the Seconds between Snapshot configuration items. This controls how often the CloudCore™ Meraki Camera Capture application will poll each configured Meraki camera.

> ****Snapshot Delivery Rate****
>
> The frequency at which camera snapshots are sent can vary depending on several factors, including the camera model’s performance, the available internet bandwidth, and cloud processing times. On average, snapshots can be delivered at the fastest at a rate of about one image every 2 seconds. This rate may differ slightly depending on the specific camera model in use. If your use case requires real-time video analysis or faster response times, we recommend using the camera’s RTSP stream along with local processing tools (EdgeFlow) to ensure more immediate access to video data. We recommend to set a minimum interval of 20 seconds between snapshots to avoid oversampling and ensure higher-quality training results.

![](../../../assets/media/images/meraki-api-advanced-setup-guide-2023-image-y8vfkfgv.png)

4.4 Scroll down to the Integrations section:

![](../../../assets/media/images/meraki-api-advanced-setup-guide-2023-image-4ykp9i1a.png)

4.5 Output subjects are automatically created for each camera source for convenience. The subject name is initially set to “Meraki camera,” plus the camera's name as specified in the Meraki dashboard at the time of app creation. You can change these subject names at any time. For reference, the description of the created subject contains the camera’s unique serial number.

![](../../../assets/media/images/meraki-api-advanced-setup-guide-2023-image-13x5zg2m.png)

4.6 The camera image snapshots will be associated with their corresponding output subject, enabling these images to be used

for application creation as with any other image data source in the Cogniac system.

![](../../../assets/media/images/meraki-api-advanced-setup-guide-2023-image-ebotmusw.png)

## 5. Training Models for MV Cameras

The Cogniac CloudCore™ Detection application type (also known as “Box Detection”) can create trained models that target execution on Meraki MV cameras. Contact Cogniac Support if your use case requires other Cogniac application types executing on the camera.

To configure an application to target Meraki MV cameras, place the box detection application in a CloudCore™ application pipeline immediately downstream from a Meraki Camera Capture application, as seen below:

![](../../../assets/media/images/meraki-api-advanced-setup-guide-2023-image-8oxspia1.png)

> Note:
>
> The box detection application must be immediately downstream from the camera capture application for the application to target the Meraki cameras automatically.

- This configuration causes the box detection app to train and release in CloudCore™ models compatible with the Meraki MV hardware. In addition, new models released in CloudCore™ also result in the newly released model being pushed to all relevant MV cameras specified in the Meraki camera capture app automatically.
- It may take several minutes for models to be updated on camera after release within the CloudCore™ system. Please check the status of the camera on the Meraki Dashboard.
- Additional mechanisms for explicitly controlling the version of a model running on a camera will be implemented as a Q2 2022 road map item, potentially utilizing the existing CloudCore ™ Deployment Workflow management framework.
