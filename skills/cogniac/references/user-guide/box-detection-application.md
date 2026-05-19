# Box Detection Application

## Box Detection Application

A Box Detection application boxes regions of interest associated with a subject in each input media item. Zero or multiple regions of interest may be identified for each subject.

## Creating a Box Detection Application

A Box Detection applications require the following fields:

- An application name, e.g., 'License Plate Boxer'.
- A list, output\_subjects, with a single subject to identify within the input media, e.g., 'license\_plate'.
- An optional list, input\_subjects, of one or more subjects to store input media. It can be output subjects from other Cogniac applications.
- An integer, max\_boxes, identifies the maximum number of box regions to detect.
- A float value, iou\_threshold, is used to decide whether a predicted box overlaps enough with the ground truth box with respect to Intersection over Union (the area of overlap between the bounding boxes divided by the area of union)
- A float value, nms\_threshold, denotes the non-maximum suppression, a threshold used to decide whether to consider boxes that significantly overlap each other to be the same box (the box with the highest detection probability is kept).

Additionally, you can see the complete Box Detection app creation flow → [[Here]](/docs/creating-a-box-detection-application).

To view additional, optional application creation fields and their default values, see [Applications - Create](/docs/applications-create).

## Box Detection Feedback

When a subject is positively associated with a media item in a detection application, the subject-media association must be accompanied by the application-specific data, or app\_data\_type, box\_set, which identifies a list of box regions, for more information on application-specific data and the valid format of box\_sets.

When the subject is not positively associated with the media item, no additional application-specific app\_data is passed.

Detection Boxes and Focus Areas

As mentioned previously, the output of a Cogniac application can be used as input to another application for creating more complex visual recognition tasks. The applications that accept the output of other Cogniac applications are sometimes referred to as "downstream" applications, as they focus primarily on subject media that has specifically been processed and filtered by one or more applications before being processed by the downstream application.

When an application outputs subject media with detection boxes in its app\_data, any downstream applications that accept the detection output subject media will process only the portions of the media that have been positively identified with the subject. This is accomplished through the concept of subject-media focus areas. Subject-media focus areas are box regions, or in the case of video media, ranges of frames, that identify subregions of the whole media to be processed by the handling application instead of the whole media object. Detection application output app\_data box\_sets are transformed to subject-media focus areas before being fed to downstream applications. For more information on focus areas, see Subject Media Associations.
