# Segmentation Application

## ****Segmentation types****

1. ****Instance segmentation**** involves creating a segmentation mask for each distinct object, distinguishing between individual instances of objects within the same class. This level of granularity is valuable for precise object counting, tracking, and interaction analysis. For example, in Robotics - it can help identify and differentiate multiple objects of the same type in a cluttered environment. In Retail - it can improve store layout and customer experience by providing personalized recommendations and targeted discounts. ![](../../../assets/media/images/segmentation-application1-image-fzwrmtet.jpg)
2. ****Panoptic segmentation**** aims to label all pixels in an image, including "stuff" and "things," creating a segmentation map of the entire image and segmentation masks for each distinct object. It unifies semantic and instance segmentation into a single framework, benefiting applications like scene understanding and urban planning. Deep learning models, such as convolutional neural networks (CNNs) and Panoptic FPN, have demonstrated remarkable performance in achieving these segmentation tasks.

   ****![This image depicts panoptic segmentation which is creating the segmentation map of an entire image and segmentation masks of each distinct object, combining semantic and instance segmentation elements.](../../../assets/media/images/segmentation-application1-image-p5eay9xe.png)****

## ****Segmentation application****

Segmentation applications divide images into multiple regions or segments, making it easier to analyze specific objects, boundaries, or areas. The segmentation application is created to facilitate instance and panoptic segmentation by generating masks for each instance within every class.

****\*Currently, the SAM Feature is beta-ready and available upon request.****

![](../../../assets/media/images/image%28200%29.png)

****Cogniac uses RLE to store the masks.****

RLE, or Run-Length Encoding, is a simple form of data compression that replaces sequences of the same data value (runs) with a single value and a count. For example, instead of storing "AAAABBBCCDAA" as-is, RLE would encode it as "4A3B2C1D2A." We compress RLE masks into [LEB128](https://en.wikipedia.org/wiki/LEB128) format.

****Effectiveness of RLE:****

1. ****Simplicity****: RLE is easy to implement and understand, making it a good choice for basic compression tasks.
2. ****Efficiency with Repetitive Data****: RLE works particularly well with data that has long runs of repeated values, such as simple graphics or certain types of text files. It can significantly reduce file size in these cases.
3. ****Low Computational Overhead****: Since RLE only requires counting and storing runs, it has low computational demands, making it efficient for both encoding and decoding.
4. ****Lossless Compression****: RLE is a lossless compression technique, meaning that the original data can be perfectly reconstructed from the compressed data.

## ****Keyboard shortcuts****

The Segmentation application now detects the user's operating system and displays keyboard shortcuts tailored to their platform (e.g., macOS or Windows). These shortcuts are available for the most common actions, helping users provide feedback faster and more accurately.

- Below are the keyboard shortcuts supported by Mac OS

![](../../../assets/media/images/Screenshot%202025-06-20%20at%201.07.42%E2%80%AFPM.png)

![](../../../assets/media/images/Screenshot%202025-06-20%20at%201.07.27%E2%80%AFPM.png)

- Below are the keyboard shortcuts supported by Windows

![](../../../assets/media/images/Screenshot%202025-06-21%20002228.png)

![](../../../assets/media/images/Screenshot%202025-06-21%20002324%281%29.png)

## ****How to provide feedback****

Once users open the Segmentation application to provide feedback, they should click the '****Add Instance****' button needs to be selected to add an instance. They will then be able to mark the area of interest. By leveraging an advanced Segmentation application, we can accurately label the dice area for this case. The segmentation application currently supports only 'Best F1' Release Metrics. Users must select the ****'Submit Feedback****' when instances are added and ready to Submit.

![](../../../assets/media/images/image%28201%29.png)

Currently, there are two available methods for providing feedback. Instances can be created using the ****SAM annotate tool**** which allows for easily marking the instance masks, thereby saving time, or using the ****Brush tool (manually)****.

1. ## ****Using the SAM annotate tool****

   The SAM annotate tool uses the Segment Anything Model in the backend to assist users in providing feedback. The user can click (Point-Prompt) anywhere on the image, and SAM provides candidate masks. SAM tries to capture the object under the point using a mask.

<iframe src="https://www.iorad.com/player/2523075/Preview-staging-Cogniac---How-to-Add-instance-using-the-SAM?src=iframe&oembed=1" width="100%" height="500px" style="width:100%;height:500px;border:none;" allowfullscreen></iframe>

2. ## ****Using the Brush tool****

Users can create a mask entirely using a paintbrush or edit the masks suggested by SAM.

<iframe src="https://www.iorad.com/player/2523092/Preview-staging-Cogniac---How-to--Provide-Feedback-in-Segmentation-App-using-the-Brush-tool?src=iframe&oembed=1" width="100%" height="500px" style="width:100%;height:500px;border:none;" allowfullscreen></iframe>

3. ## ****Using the Polygon tool****

   - Unlike bounding boxes, polygons can more precisely follow an object's boundaries, capturing its exact shape for non-rectangular objects.

****# Use cases:****

This technique is particularly useful for annotating objects with irregular shapes like coastlines, medical scans, or intricate details in natural images like the brush tool but with increased speed and convenience. Brush and eraser tools can be used to adjust the annotated area in conjunction with the polygon tool.

****## Usage Instructions****

Go to instance edit mode (new or existing instance):

- click to start polygon or use <kbd>E</kbd> (for Windows users only)

- add points using left mouse button

- to undo a point press <kbd>Z</kbd> (Windows)

- double-click or press <kbd>Space</kbd> (for Windows) to finish polygon and rasterize

- to delete rasterized layer and start again press <kbd>C</kbd> (Windows)

<iframe src="https://www.iorad.com/player/2523121/Preview-staging-Cogniac---How-to-provide-Feedback-in-Segmentation-App-using-the-Polygon-tool?src=iframe&oembed=1" width="100%" height="500px" style="width:100%;height:500px;border:none;" allowfullscreen></iframe>

4. ## ****Introducing the Polygon Fill Tool****

In certain situations, users may need to create more complex shapes—such as rounded or square forms—for their annotations. The Polygon Fill tool is particularly effective for these scenarios, enabling users to create customized masks tailored to their specific needs.

To create a polygon fill mask:

- Add a new instance.
- Press ****‘r’**** or click the designated button shown in the image below.
- Draw the instance mask using a shape that best fits your requirements.

## ![](../../../assets/media/images/image%28198%29.png)

5. ## Introducing the Polygon Erase Tool

Users can now not only create custom-shaped masks using the ****Polygon**** tool, but also remove them using the ****Polygon Erase**** tool. This is especially helpful in cases where a mask has been overdrawn—for example, when using the Polygon or Polygon Fill tools.

To remove a custom-shaped mask:

- Press ****‘Shift’ + ‘r’**** to activate the Polygon Erase tool.
- Draw the polygon shape you wish to remove.

![](../../../assets/media/images/image%28199%29.png)

## ****Denoising and how it works****

The denoising is a frontend feature that allows users to easily remove all pixel groups that are smaller than the Denoise pixel group size, eliminating the need for manual cleanup with the eraser tool. By automating the removal of these small pixel clusters, the feature also speeds up the process of fine-tuning and polishing the mask.

For Example if the Denoise size is set to 20 pixels pixel groups with 19 pixels or less will be cleared.

![](../../../assets/media/images/image%28194%29%281%29.png)

![](../../../assets/media/images/image%28195%29.png)

Once the user has finished marking the Instance Mask, they need to save the instance by clicking the button Save or Save & New. Unless the instance has not been saved or deleted (Cancel button), the user won’t be able to Submit Feedback for the selected media.

Once the user submits the feedback, we fine-tune SAM to the user's inputs. We have 2 activities associated with it under the Summary tab of the application:

1. ****Label Model Trained:**** This activity updates the new label model (SAM) that was trained to improve the labeling experience.
2. ****Label Model Released:**** This activity provides an update on whether we have some new best-winning label models. From here on, we use this model to assist the user while labeling.

****![](../../../assets/media/images/segmentation-application1-image-f8nt7zuh.png)****

## Currently supported pipelines

1. Segmentation application downstream to Classification application

![](../../../assets/media/images/segmentation-application1-image-juvpmcpt.png)

2. Segmentation application downstream to Detection Point application

![](../../../assets/media/images/segmentation-application1-image-rj0gnzx2.png)

3. Segmentation application downstream to Static Count application

![](../../../assets/media/images/segmentation-application1-image-em23y47r.png)

4. Box Detection application downstream to Segmentation application

![](../../../assets/media/images/segmentation-application1-image-ah51wdlh.png)
