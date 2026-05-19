# Application Types

## Application Types

The Cogniac system is designed to automate many visual observation tasks. This flexibility allows complex visual processing tasks to decompose into simpler operations. Applications form the basic building blocks of media processing within the Cogniac system. Many application types are based upon deep convolutional neural networks, but other more simple applications also have roles to play. The application types currently supported by the Cogniac system developer include:

- ****Classification****

  - You can view more about the Classification App → [[Here]](/docs/classification-application)
  - To check the Flow on the Classification App Creation, see → [[Here]](/docs/creating-a-classification-application)
- ****Detection****

  - See more about the Detection App → [[Here]](/docs/detection-application)
  - Check the Detection App Creation flow → [[Here]](/docs/creating-a-detection-application)
- ****Point Detection****

  - More details about the Point Detection app can be found → [[Here]](/docs/point-detection)
  - View the entire Point Detection app creation flow → [[Here]](/docs/creating-a-point-detection-application)
- ****Box Detection****

  - More information about the Box Detection app → [[Here]](/docs/box-detection-application)
  - See how to create a Box Detection application → [[Here]](/docs/creating-a-box-detection-application)
- ****Area Detection****

  - You can find how the Area Detection app works → [[Here]](/docs/area-detection-application)
  - Complete flow on the Area Detection app creation → [[Here]](/docs/creating-an-area-detection-application)
- ****Count Application****

  - See details about the Count Application → [[Here]](/docs/count-application)
  - To find out how to create the Count Application, check → [[Here]](/docs/creating-a-count-application)
- ****Object Character Recognition (OCR) application****

  - OCR App details can be found → [[Here]](/docs/optical-character-recognition-ocr-application)
  - See how to create an OCR application → [[Here]](/docs/creating-an-optical-character-recognition-app-ocr)
- ****Segmentation application****

  - Segmentation app details can be reviewed → [[Here](/docs/segmentation-application)]

  ## Application Specific Data

Some application types use the concept of optional application-specific subject-media data, or app\_data that identifies the relationship between the subject and media object in the context of the observation task performed by that application, such as box region areas in detection applications, and a range of frames in detection full-frame applications.

> The Cogniac system supports the following application data types:
>
> ****box\_set**** - A list of box regions corresponding to the subject. A box region is defined as:
>
> ```plaintext
> {
>     “box”:            (dictionary of integers) “x0”, “x1”, “y0”, “y1”
>                           Values correspond to pixel offsets in the media item
>                           (x0, y0)  upper left corner of bounding box
>                           (x1, y1) lower right corner of bounding box
>                           Note that x1 must be greater than x0
>                           and y1 must be greater than y0
>
>     “probability”:  (optional) (float) probability for box
> }
> ```
>
> ****segment\_list**** - A list of video frame segments corresponding to the subject. A segment is defined as:
>
> ```plaintext
> {
>     “segment”:  (dictionary of integers) “f0”, “f1”
>                        f0 & f1 correspond to the frame offsets in a video media
>                        (frame count starts at 0)
>                        f0 is the first frame in the media item segment with the subject
>                        f1 is the last frame in the media item segment with the subject
>                        Note that f1 must be greater than, or equal to f0
>
>     “probabilities”:  [ordered list of per-frame model output probabilities]
>                              The first list entry corresponds to prob for the frame at f0
>                              The last list entry corresponds to prob for the frame at f1
>                              Note the length of the list if present must equal (f1 - f0 + 1)
> }
> ```
>
> ****ocr**** - A string representing the characters detected.
>
> ```plaintext
> "01234"
> ```
>
> ****count**** - A float (>= 0) representing the number of occurrences of the subject detected.
>
> ```plaintext
> 2.5
> ```
