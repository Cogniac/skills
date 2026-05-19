# Cogniac Box Detection Best Practices

## Objective

This document outlines best practices for providing feedback ( Labeling ) in box detection applications within the Cogniac system and emphasizes the importance of adhering to these best practices.

## Overview

The Cogniac "Box Detection" application is highly effective at analyzing high-resolution images to identify small or subtle objects, defects, or conditions. It generates bounding box predictions around areas of interest. As with all deep learning tasks, the accuracy of this application relies on the quality of the labeled consensus data used for training and evaluating the model.

## Accuracy: Influencing Factors

The major factors that influence the resulting application accuracy include:

● Count of labeled consensus images available for training, including positive and negative examples.

Having more images is beneficial, but there's a limit. Generally, a good baseline performance can be achieved with 20 to 200 positive and negative images. However, depending on the sources of variation mentioned, you may need an additional 200 to 2,000 training images in some cases to optimize application performance.

● Size of the object, condition, and any defects are important, particularly regarding image size.

Identifying small objects, defects, or conditions in large images is significantly more challenging than locating larger items in smaller images. Small objects may necessitate a greater number of training images, particularly if the background of the images exhibits considerable variation.

● The natural variation in the object, its condition, or any defects of interest.

Objects, defects, and conditions with greater natural variation require more training data to resolve than those with less natural variation.

● The natural variation in the background of the image.

Images with significant background variation may need more training images to minimize false detections.

● Image variations encompass differences in object size, angle, color, and lighting.

The greater the variation in imaging conditions, the more training images are needed to reach a specific accuracy level.

● The visual clarity of the objects, defects, or conditions of interest in relation to the background.

Objects with clear and distinct edges are easier to detect and box than amorphous defects or conditions.

● The challenge of this visual task involves considering visual context for accurate bounding box placement.

Cogniac box detection applications can learn to take visual context into account when making bounding box predictions; however, this is a more challenging visual task that may require additional training data.

● Availability of challenging negative data.

Cogniac systems utilize hard negative data—incorrect detections made by models that users have corrected—to improve model performance. Relying solely on pre-labeled data prevents the mining of hard negative data. The most effective feedback strategy involves providing initial feedback, waiting for an improved model, and then offering additional feedback.

## Best Practice for Bounding Boxes

1. Why it Matters?
   In addition to the sources of variation in objects and images mentioned earlier, users can unintentionally introduce further variation in bounding box labeling by not following the best practices outlined in this document. Specifically, discrepancies in the size of the user-defined bounding boxes compared to the actual objects, defects, or conditions can negatively affect the application's accuracy. This unintended variation can increase the amount of training data needed to attain the desired level of accuracy. Best Practices Recommended Cogniac best practices to minimize this source of collateral variation are as follows:

2.1. Size of Boxes For objects with distinct external edge boundaries, position the bounding boxes so that all edges of the object are enclosed within them. Each bounding box should encompass the entire item while leaving a few pixels of buffer space between the box and the nearest edge of the object. The bounding boxes should fit reasonably snugly around the object, nearly touching it at four or more points. In some instances, the bounding box may cover other objects, which is acceptable. As long as it fully covers the object of interest with minimal extra space around the edges, the labeling adheres to best practices.

![image.png](../../../assets/media/images/image%281%29.png)

Figure 1. This bounding box around scissors is well labeled as it fully encircles them while fitting snugly around the edges.

![image.png](../../../assets/media/images/image%282%29.png)

Figure 2. Avoid using multiple boxes to represent a single instance of an object. This is a common mistake that users make in an attempt to reduce the amount of background included in a label. Doing so introduces unnecessary variability and can lead to confusion in applications.

![image.png](../../../assets/media/images/image%285%29.png)

Figure 3. Boxes that are too small (right) or too large (left) do not follow the best practices for box labels.

2.2. When labeling multiple identical objects in a single image, it is important to provide a separate bounding box for each distinct object. Be sure to follow the guidelines mentioned above to ensure accurate labeling.

![image.png](../../../assets/media/images/image%286%29.png)

Figure 4. This image features four clamps. Each clamp should be enclosed within its own bounding box that includes the complete object. Overlapping boxes are permissible, as shown.

![image.png](../../../assets/media/images/image%287%29.png)

Figure 5. Do not use a single large box to bound multiple objects of the same type.

2.3. “Angled” Objects

A common question arises around objects that are angled in an image. “Do I still draw a box around this, even though there is all this extra space?” The answer is “Yes!”

![image.png](../../../assets/media/images/image%289%29.png)

Figure 6. Even though these boxes look very different, these are both valid labels for this level. If an item is angled in the image, continue following the best practice of drawing a complete box encompassing the entire object.

![image.png](../../../assets/media/images/image%2811%29.png)

Figure 7. Do not use multiple boxes to “adjust” for angled items. Never use multiple boxes to represent a single instance of an object to minimize the amount of background captured in a label. It introduces confusing variability to the applications.

2.4. Partial Objects Labeling items that are not fully contained in the image is generally not recommended. There may be some instances where you have received specific instructions from the Cogniac team regarding partial object labeling. If you have not received specific instructions to label partial objects, please refrain from doing so.

![image.png](../../../assets/media/images/image%288%29.png)

Figure 8. The pair of scissors is not fully visible in the image. Therefore, it should not be labeled.
