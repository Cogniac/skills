# Detection Application

## Detection Application

- A Detection application, much like a Classification application, identifies subjects of interest in media. However, in a Detection application, the association of each output subject to a media item is assessed independently. So, a single media item can have strong associations with multiple subjects; e.g., an image can contain both a cat and a dog, with subject-media association probability around 1.0 for both subjects. With Detection applications, any number of subjects can be present, or media can have a strongly negative association with all subjects, allowing for more complex subject-media relationships than a straightforward classification application. The maximum number of output subjects supported is 20.
- A Detection application is an appropriate choice when a single subject-media association is insufficient for the needs of the application’s end product or when it is not guaranteed to find even a single output subject in the input media data. For example, unlike a Classification application, a Detection application with one output subject helps filter raw input media into relevant and irrelevant subjects to inject relevant media into other applications further.

One of the most common uses of Detection applications is as a 'filter' for a relatively rare subject.

## Creating a Detection Application

Detection applications require the following fields:

- An application name, e.g., ****'Car Detector'****.
- A list, output\_subjects, of one or more subjects to identify within the input media, e.g., ****'car'****.
- An optional list, input\_subjects, of one or more subjects to store input media. It can be output subjects from other Cogniac applications.
- An optional boolean, ****feedback\_all\_positives****, when ****True****, surfaces all positive subject-media associations for user feedback. This field is best used for applications with rare subjects to ensure all positive detections get feedback.

To view additional, optional application creation fields and their default values, see [Applications - Create](/docs/applications-create).

Detection Subject-Media Associations

In contrast to Classification applications that are guaranteed to output exactly one positive association between a media item and output subject, output media from Detection applications are related positively or negatively to every output subject.

When processed by a Detection application, media items are tagged with a more complex series of positive and negative relationships with the application's output subjects. Hence, an application with a single output subject will generate two sets of subject-media associations: positively correlated media and negatively correlated media.

You can also view the entire flow on the Detection application Creation → [[Here]](/docs/creating-a-detection-application).

## Detection Feedback

Detection applications identify separately the strength of each association between one or more subjects in a media item. When providing feedback in a Detection application, it is a best practice to remember to weigh the relevance, both positive and negative, of each output subject individually against the provided media.

False Subject-Media Associations

In Detection applications, subjects, and media can be negatively associated just like a subject is positively associated with media. If no output subjects are sufficiently represented in a media item, providing False feedback for every subject is perfectly valid.
