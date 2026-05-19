# Best Practices for Camera Selection and Positioning

The purpose of this document is to explain how to design an effective optical system that enhances Cogniac’s platform performance and reliably detects defects and objects of interest.

The placement and configuration of cameras play a crucial role in determining the accuracy, reliability, and effectiveness of a system. A well-designed setup ensures that the system can capture essential information from the scene and process it effectively. Additionally, proper camera placement and configuration can enhance system efficiency, while also reducing hardware, processing, and maintenance costs.

## Camera Selection

#### Target Size and Distance

When selecting a camera for a computer vision application, it is crucial to consider two key factors: the size of the target and its distance from the camera. These factors depend on the lens, the camera itself, and the necessary camera settings to ensure consistent and reliable detection by the Cogniac platform.![](../../../assets/media/images/best-practices-for-camera-selection-and-positioning-image-qgcakhsl.jpg)

![](../../../assets/media/images/best-practices-for-camera-selection-and-positioning-image-i8ghutj1.jpg)

## Camera Lens

A camera lens is a component that allows light to focus within the camera. The focal length of a lens refers to its magnification capability; a higher focal length results in greater magnification, enhancing the camera's ability to capture smaller or distant objects. However, this comes with a trade-off: a higher focal length reduces the overall scene captured. In contrast, lenses with shorter focal lengths provide a wider field of view (FOV) but with less detail compared to long focal length lenses. Additionally, some lenses feature variable focal lengths, which increase the versatility of the camera.

 ![](../../../assets/media/images/best-practices-for-camera-selection-and-positioning-image-8da2p580.jpg)

## Target Resolution

Although a lens with a small focal length captures a wider view of a scene, it does not necessarily gather more data than a camera with a longer focal length. The amount of data collected in a scene is ultimately determined by the camera sensor. The sensor consists of pixels that convert incoming light into a digital format. The total number of pixels on a camera sensor is referred to as its resolution.

![](../../../assets/media/images/best-practices-for-camera-selection-and-positioning-image-6kqepkwu.jpg)

The resolution of a camera indicates the number of pixels on its sensor. Higher resolution means targets contain more pixels, resulting in increased detail.

For reliable detection by the Cogniac system, a target must have a minimum height and width of at least 20 pixels. This requirement can be determined using the target's height, the distance to the target, the lens's focal length, and the pixel size on the sensor. For detailed instructions on how to calculate the height of a target in pixels, please refer to Appendix A.

## Field of View![](../../../assets/media/images/best-practices-for-camera-selection-and-positioning-image-j048afcj.jpg)

The Field of View (FOV) refers to the horizontal and vertical area that the camera captures in a single image. Each combination of camera and lens has a specific viewing angle, which restricts the extent of the field of view that can be captured.

The camera sensor and lens must work together to create a field of view that encompasses the entire scene while ensuring that the subjects contain enough pixels for accurate detection. When the scene is too large to be captured by a single camera's field of view, multiple cameras will be necessary. If the images from two cameras are to be stitched together, they must be identical and have at least a 25% overlap in their fields of view.

## Distortion

![](../../../assets/media/images/best-practices-for-camera-selection-and-positioning-image-wq58gw30.jpg)

The lower the focal distance of a camera is, the more severe the image distortion becomes. For lenses with a focal length less than 5 mm, distortion becomes noticeable enough to impact the performance of the Cogniac platform. This warping makes objects in the center of the frame look very different from objects at the edges.

There are some applications where ultra-wide angle cameras can maximize the field of view without impacting performance. One example is tracking the state of something not moving (e.g. how much grain is in a hopper). In this case, the distortion between the edges and the center will still be there, but the distortion of the target will be the same between the training data and inference data.

If the target (or targets) are all contained in the center of the frame, the field of view can be cropped and the ultra-wide lenses can still be utilized. Additional system training can also mitigate the decreased performance caused by distortion.

## Camera Configuration

#### Depth of Field

All cameras have limitations around their minimum and maximum in-focus distance, also known as the ****Depth Of Field****. Objects inside of the depth of field will be in focus and objects outside of it will be blurry.

 ![](../../../assets/media/images/best-practices-for-camera-selection-and-positioning-image-3mkp0zm1.jpg)

A key element of a lens is the ****aperture****. The aperture, also known as the f-stop, is a circular opening that opens and closes to allow different amounts of light into the sensor. The aperture has the most control over the depth of field of an image.

The smaller the opening, the larger the depth of field becomes. When the aperture is smaller, there is less light getting to the sensor, so more light in the scene is required. In some use cases, a shallow depth of field that blurs the background can help the Cogniac platform focus on the subject matter in focus.

#### ![](../../../assets/media/images/best-practices-for-camera-selection-and-positioning-image-chgbclfi.jpg)

#### Target Speed

The shutter of a camera is the device that is responsible for freezing the motion of a target. The slow-mo guys made a great video of a rolling shutter in action [here](https://www.youtube.com/watch?v=CmjeCchGRQo). A higher shutter speed can capture higher speed targets and keep them in good focus, but requires more light on the target.

Cameras that utilize auto-exposure typically use the shutter speed (also called exposure time) to get good exposure. To compensate for a dark scene, the shutter speed will be reduced, possibly to a degree that moving targets become blurred. For reference, to take a good picture from the sidewalk of a car going ~30mph, a shutter speed of 1/60 is needed. Supplemental lighting is recommended in applications where ambient light will not be sufficient for proper exposure and shutter speed.

 ![](../../../assets/media/images/best-practices-for-camera-selection-and-positioning-image-t5fgai1l.jpg)

In a use case where the target will be moving at a constant and repeatable speed, the shutter should be fixed so the images are repeatable as well.

### Lighting

#### Exposure

Sufficient lighting is essential to getting quality images of the target for the Cogniac platform to train and perform well. Illumination plays a critical role in determining the contrast, depth of field, and sharpness of the image. The target needs to be adequately lit so that the features of the target can be distinguished, also known as good ****exposure****. The camera configuration that can be used is highly dependent on if there is adequate lighting available in a scene with low light conditions putting the most constraints around them.

![](../../../assets/media/images/best-practices-for-camera-selection-and-positioning-image-8m3p1otd.jpg)

Most cameras can auto-compensate for variation of lighting conditions, but if the use case will need to be active in a wide range of lighting conditions, like at night and during the day, considerations around configuration capabilities, supplementary lighting and additional training need to be addressed.

#### Auxiliary Lighting

If additional lighting is needed in an application, there are additional hardware considerations and requirements. Fluorescent, quartz halogen, and LED lighting are the most common lighting used in machine vision applications. In settings where the application is lacking in ambient light, simple diffuse lighting in the form of street lamps or overhead lighting is commonly used. In more specific applications like manufacturing inspection, lights are arranged in specific ways to highlight the target in a way that best differentiates it from its surroundings.

When integrating the lighting with a camera (or cameras), additional hardware is required. These can include light controllers (like a PLC), power supplies, cables and connectors, mounting hardware and a system triggering device. Vision system integrators can help in the configuration and install of these devices to ensure the LEDs operate in sync with the camera along with the rest of the system.

#### Target Contrast

If the subject and the background have similar colors or textures, it can be difficult for the system to separate them and identify the subject accurately. In such cases, the system may make errors in its analysis, leading to incorrect decisions or classifications.

The contrast between the subject and the background is necessary for a machine vision application because it helps the machine to distinguish between the subject and the background. Unique light and camera mounting angles, different light wavelengths and even colored filtering are all techniques that can be used to increase contrast.

## Camera Positioning

#### Objects Covering

Objects like foliage and furniture can impede the camera’s line of sight of a target. In order to consistently detect a target, the target needs to be at least 60% to 70% visible to the camera. The smaller the object is, the greater the need is for complete visibility.

#### Optimized Target Capture

It is important to place the camera in a position with comprehensive scene coverage. A camera looking at types of cars will more efficiently collect information if it is placed high up and can see many cars at once compared to if it is placed at street level and can only see one car at a time.

Targets should also be viewed at an angle that highlights their unique characteristics. An application looking at people riding a bike or a scooter will not perform well if it is mounted high up and looking straight down. A camera should be set up to see the side profile of the bikes and scooters to be able to detect and differentiate them accurately.

#### Poor Weather / Looking into the Sun

In outdoor applications, poor weather conditions can cover targets in ways that won’t allow detection. Some examples include fog blurring a target, rain distorting car headlights and taillights, and snow decreasing overall visibility.

It is also important to not position a camera looking into the sun at any time of the day or year. The sun’s direct brightness will overtake a camera’s auto-exposure settings and make the foreground objects extremely dark and background objects extremely bright.

#### Cleanliness

The cleanliness of a camera lens is essential to its consistent and effective performance. System performance will decline over time if the camera is placed in an environment where particulates can build up on the lens. Dust and particulates can also get into the camera components and reduce their ability to cool, reducing the hardware's performance and lifespan.

To prevent this, regular cleaning of the cameras should occur. Additional hardware like camera enclosures, camera placement in a covered area, or air blowoff systems all work to reduce the maintenance required to keep the camera clean.

## Scenarios

The following scenarios bring vision system design considerations together to set up the hardware and mounting requirements for different use cases.

### Supermarket

#### Use Case:

The number of people leaving a supermarket with a bag or cart (meaning they purchased something) and the number of people leaving without purchasing anything.

#### Camera Location:

They are mounted above the exit door(s) looking into the store approximately 3 meters from people leaving the store at an angle of 45 degrees.

#### Camera Lens:

A 10mm lens will result in a shopping bag 3 meters away having a pixel height of 595 pixels on an average image sensor. The field of view is wide enough to be able to see large shopping carts in the frame fully, but it will also have enough resolution to see shopping bags well.

#### Shutter Speed:

Greater than 1/60 to freeze the motion of the people walking out the door.

#### Aperture:

f/4 for a large depth of field, but it can still work off of the artificial illumination of the store.

## Sidewalk Usage

#### Use Case:

Determine the usage of sidewalks. Identify if people are using the sidewalk for walking, biking, or scootering at night and during the day.

#### Camera Location:

It was mounted on a light pole ~15 feet high and pointed towards the opposite side of an intersection. The camera should be mounted above or on the opposite side of the pole as the light to prevent light interference when it turns on.

#### Camera Lens:

A 6mm Lens will provide a large field of view allowing you to see a lot of the sidewalk in the scene. People are relatively large targets to detect and even more significant when combined with a bike or scooter, so moderate magnification is sufficient.

#### Shutter Speed:

The lowest shutter speed the camera should go to is 1/60th second. The slower 1/60th shutter speed will be used at night when there is only artificial illumination from the street light available and a faster shutter speed will be used during the day when there is ample sunlight.

#### Aperture:

f/2.8 during the day to get more depth of field and f/1.4 at night to allow more light in.

## Cleaning Solution Bottle

#### Use Case:

Looking at the fullness level of a clear bottle of cleaning solution coming off from the manufacturing line.

#### Camera Location:

Placed beside the manufacturing line ~1 meter away, looking at the necks of the bottles where the fullness of the liquid contents is expected to be.

#### Camera Lens:

A 65mm lens will frame the top of the bottle to see where the fill line should be while leaving a safe distance from the machinery for the camera system.

#### Shutter Speed:

The camera should be triggered based on the line speed of the bottles using a device like an encoder. The shutter speed (or exposure time) will need to be fast to keep up with the speed of the manufacturing line and should be fixed.

#### Aperture:

f/1.4. The front and the back of the bottle should be in full focus, but blurring contents in the background will simplify the scene.

#### Lighting:

A diffuse light should be placed behind the bottles so that the light is shining through the bottles and to the camera.

## Appendix A

The ****height of a target in pixels**** can be calculated using this formula:

![](../../../assets/media/images/best-practices-for-camera-selection-and-positioning-image-pukuqq3f.png)

h: Image Height on Sensor (pixels)

H: Height of Target (mm)

F: Focal Length of the Lens (mm)

D: Distance to the Target from the End of the Lens (mm)

Px: Sensor Pixel Size (μm)
