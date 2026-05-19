# Area Detection Application

Area detection is best suited for visual tasks where the object to be identified has a highly irregular shape or pixel-level detail in detection is required. A common example would be detecting a crack in some objects. Area Detection is also a good choice for visual tasks where positive examples are limited, as there is more training information contained in area labels.

To view additional, optional application creation fields and their default values, see [Applications - Create](/docs/applications-create).

You can also view the entire flow on the Area Detection application Creation → [[Here]](/docs/creating-an-area-detection-application).

●      Setting up the new application type

○      If you are converting an existing Area Detection app:

Existing labels can be converted to the new label format by the Cogniac team. Suppose your systems are utilizing the output of the current Area Detection results format. In that case, Cogniac can also provide code samples that will convert the output back to bounding boxes to integrate the app into your code base seamlessly.

○      If you are creating a new Area Detection App:

Detection Area requires an input and output subject. There are no custom settings for this app.

### Updated Label Interface

The Area Detection app provides an updated labeling interface for painting the areas.

![](../../../assets/media/images/image%2828%29.png)

**Use a paintbrush to quickly and intuitively label the pixels of the object you are trying to identify**

![](../../../assets/media/images/image%2827%29.png)

![](../../../assets/media/images/image%2836%29.png)

![](../../../assets/media/images/image%2837%29.png)

**Different sized brushes can be used to control the level of detail in labeling**

![](../../../assets/media/images/image%2838%29.png)

![](../../../assets/media/images/image%2839%29.png)

**Label opacity can be adjusted to provide visibility to the item being marked**

![](../../../assets/media/images/image%2840%29.png)

![](../../../assets/media/images/image%2841%29.png)

**Easily erase any mistakes**

![](../../../assets/media/images/image%2835%29.png)

**Detection Area V2 is ideal for applications which require highly detailed labels**

## Performance Calculations

The Area Detection application uses the same metrics as its version 1 for calculating model performance. The metric counts every individual pixel to determine TP, FP, and FN. The following table shows how a pixel is counted toward TP, FP, and FN.

|  |  |  |
| --- | --- | --- |
|  | The pixel is masked in the ground truth | The pixel is masked in the detection result |
| TP | Yes | Yes |
| FP | No | Yes |
| FN | Yes | No |

## New Detections Output Format

A PNG represents the output for the Area Detection app. The detection output will look similar to other applications, except for the app\_data\_type and the app\_data fields.

In summary, the PNG representation of the detected area can be interpreted by examining the pixel position on the down-sampled detection resolution and the alpha channel, which maps to the probability on a scale of 0 to 255. It is important to note that because one pixel in the detection represents an eight-pixel block in the original image, the detections do not have the same “resolution” as the original image. Therefore, Detection Areas should not be used for highly precise measurement applications.

Below is a detailed description of that portion of the Area Detection schema.

app\_data\_type: area\_mask

app\_data = {

|  |  |
| --- | --- |
| area\_mask\_png (string) | an 8-bit-depth RGBA encoding PNG serialized in base64 coding.  The alpha channel of the PNG is used to store the probability/consensus label while all the RGB channels are 0, and the values in RGB channels are currently ignored. The probability is mapped linearly to the alpha range in [0,255]. For example, for true consensus on a pixel, the pixel should have a value of 255 in its alpha channel.  The resolution of the PNG is ⅛ of the original image size. If an image dimension is not divisible by 8, the area mask png will be padded in that dimension. For example, for a 1002x1000 image, the area\_mask\_png size will be 126 x 125. |
| probability | (optional) the max probability over all the probabilities in the area mask |

## When to use?

| Use case | Type of App |
| --- | --- |
| Identifying objects without a fixed or regular shape | Area Detection |
| Pixel-level detail in the detection is required | Area Detection |
| Very few positive samples are available | Area Detection |
| The next step in the pipeline is a measurement app | Point Detection |
| Very few positive samples are available. | Box or Point Detection |
| The relative position of detections is required to be precise. | Box Detection |
| Counting discrete objects. | Box Detection |

## Current Limitations

○      Area Detection cannot consume the focus box from an upstream app as input. If an upstream application sends a focus box to the Area Detection app, the entire image will be processed by the Area Detection app.

○      Downstream applications, except custom integration apps, cannot consume the output of Area Detection.

○      The enhanced labeling interface currently only supports single-subject labeling.
