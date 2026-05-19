# Meraki AI Quick start Guide

## Objective

This guide outlines using a Cogniac CloudCore™ tenant with the Meraki  to train and deploy Machine learning models to Meraki MV cameras. This guide assumes that you have a Meraki Dashboard account and a Cogniac CloudCore tenant with Meraki features enabled. It also assumes you have MV cameras compatible with the Cogniac platform provisioned on the Meraki tenant.

## Creation of a Cogniac Box detection Application linked to Meraki Camera

Step 1: Log in to your Cogniac tenant.

Step 2: Click the blue ‘Application Builder’ tab on the left-hand side.

Step 3: Select ‘Meraki AI’ under the **Templates** section

Note: If Meraki AI is not visible under **Templates** in the Applications Builder (see Figures 1 and 2), then Meraki AI is not enabled for the tenant. Contact cogniac support for further assistance at [support@cogniac.ai](mailto:support@cogniac.ai)

![](../../../assets/media/images/meraki-ai-quick-start-guide-2023-image-z6h17zg0.png)![](../../../assets/media/images/meraki-ai-quick-start-guide-2023-image-6yuj98j6.png)

| Figure 1: Meraki enabled  tenant | Figure 2: Meraki not enabled tenant. Please get in touch with your Cogniac account team for assistance. |
| --- | --- |

Step 4: Configure Meraki credentials (API key) (first time only)

![](../../../assets/media/images/meraki-ai-quick-start-guide-2023-image-0iwl8sj1.png)

Type in the Meraki Dashboard API Key. If you don’t have the key associated with your Meraki tenant, [here](https://documentation.meraki.com/General_Administration/Other_Topics/Cisco_Meraki_Dashboard_API) is a guide on how to obtain it. The organization ID will be automatically populated if the API key has access to a single Meraki organization. If the API key has access to multiple Meraki organizations, you will need to select the organization that needs to be accessed from the CloudCore™ tenant.

Step 5: Select ‘Get Started’

![](../../../assets/media/images/meraki-ai-quick-start-guide-2023-image-h4rz29x8.png)

Step 6: Select Cameras to Use

![](../../../assets/media/images/meraki-ai-quick-start-guide-2023-image-469oj3zh.png)

For “Name”, you need to type in the name of the Meraki Camera capture application that will contain all of the images and videos collected by your cameras, which will be the input for the application, both during training and Inference.

The **Sampling Interval** in seconds is set (the default value is 60 seconds). Images will be gathered at this rate for use in training the model.

You can select as many cameras as you like, but each camera can have only one application, so be careful not to link a camera to more than one application. The machine learning models work best if all the cameras have identical optics (see Table below).

You can search/ filter the Meraki Camera to be used for the application by camera name, model, MAC address, or serial number.

Step 7: Provide a name to your application and its output subject

![](../../../assets/media/images/meraki-ai-quick-start-guide-2023-image-lx9f9v68.png)

The application and output subject names can be a description of the goal of this application (e.g., Find Self Driving Cars, Find people not wearing hard hats) or any other unique name. Once the user selects ‘Complete’, the new Pipeline can be viewed on the home page.

![](../../../assets/media/images/meraki-ai-quick-start-guide-2023-image-96vtr6kj.png)

The successfully running application will look similar to the one shown in the image below:

![](../../../assets/media/images/meraki-ai-quick-start-guide-2023-image-p79xj8ff.png)

Training for this application is covered in a separate document.

##

## Appendix A: Supported Cameras

The following Meraki MV camera models are currently supported:

|  | ****MV2**** | ****MV12WE**** | ****MV12W**** | ****MV12N**** | ****MV22 Series**** | ****MV32**** | ****MV63 Series**** | ****MV72 Series**** | ****MV93 Series**** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Focal Length [mm] | 2.8 | 2.8 | 2.8 | 3.8 | 3-9 | 1.19 | 3.3 | 3-9 | 1.6 |
| Aperture | f/2.0 | f/1.8 | f/1.8 | f/1.8 | f/1.2-2.3 | f/2 | f/2.0 | f/1.2-2.3 | f/2.0 |
| Sensor Pixel Size (μm) | 1.998 | 1.998 | 1.998 | 1.998 | 1.998 | 1.404 | 1.45 | 1.998 | 1.85 |

Table 1: The Meraki cameras supported by the Cogniac platform with their critical parameters

Most of these cameras have a short focal length, leading to images with high distortion levels. Distorted images require training images everywhere in the field of view (FOV) where detection is desired. Due to this, if possible, choose a camera with a higher focal length or have a training effort that takes care to cover your desired FOV sufficiently.

## Appendix B: Target Size and Inference Frame Rate

Small objects require more complex models and greater processing power to detect. Therefore, it’s important to know the size of the object and the processing power available to calculate the rate at which images are processed. We also need to know the target size in pixels to understand if the object will be detectable.

The supported Meraki cameras are available in ****Gen2**** and ****Gen3**** versions. They have the same optics and sensors, but the Gen3 cameras have more memory and processing power, allowing for faster processing.

The height of a target object in pixels can be calculated using this formula

![](../../../assets/media/images/meraki-ai-quick-start-guide-2023-image-89xd40qp.png)

h: Image Height on Sensor (pixels)

H: Height of Object (mm)

F: Focal Length of the Lens (mm)

D: Distance to the Object from the End of the Lens (mm)

Px: Sensor Pixel Size (μm)

****If **h** < 20 pixels, the target will be difficult to detect by our system.****

Once we know the size of the target in pixels, we can estimate the rate that the camera will publish inferences (See Table 2).

|  | Small (20 pixels) | Medium (28 pixels) | Large (42 pixels) |
| --- | --- | --- | --- |
| Gen 2 | 0.25 | 0.5 | 1.0 |
| Gen 3 | 0.4 | 0.8 | 1.6 |

### Table 2: Inference rate in frames per second (fps)

The document “Best Practices for Camera Selection and Positioning” provides more guidance on selecting the ideal camera for your situation.

Full Document, can be found here: [Best Practices for Camera Selection and Positioning](/docs/best-practices-for-camera-selection-and-positioning)

## Appendix C: Glossary

****CloudCore**** Cogniac’s CloudCore is the centralized workflow development, model training, and evaluation platform. It is a powerful, centralized hub for interacting with your entire solution.

****Tenant**** A tenant in the CloudCore system is a dedicated, isolated workspace for a particular customer, use case or end-user application. Tenants are securely isolated from each other in the CloudCore system, with each tenant having independent user lists and flexible Role-Based Access Controls.

****Inference**** Inference refers to the process of using a trained machine-learning algorithm to make a prediction. Inference can be performed on a supported Meraki MV camera.

****Model**** The Cogniac platform trains an algorithm with parameters (i.e., a Model) that allows the system to infer if an image includes the target that interests the user. The target could be the presence of a defect or a city bus, depending on the use case. This model will be uploaded to the Meraki MV camera, allowing it to make inferences on images and communicate them to the Meraki Dashboard.

****Cisco Meraki Dashboard API**** The [Meraki dashboard API](https://documentation.meraki.com/General_Administration/Other_Topics/Cisco_Meraki_Dashboard_API) is a software interface that interacts directly with the Meraki cloud platform and Meraki-managed devices.

****Subject**** A collection of images or videos. For example, a collection of labeled images from a Meraki camera is used to train a model.

We love to hear from you!

If you have any questions or comments, please email us at support@cogniac.ai
