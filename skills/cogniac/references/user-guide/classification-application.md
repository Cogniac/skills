# Classification Application

## Classification

A Classification application tags media items by identifying the single most prominent Subject from a predefined list of mutually exclusive and exhaustive Subjects. This means that each media item must apply to exactly one subject from the list, and the list can contain a maximum of 20 subjects. In other words, only one subject can be assigned to each media item presented to the classification application.

Classification of Media

All media processed by a Classification application will be associated with a single Subject. Useful Classification applications should have at least two output subjects, which must be mutually exclusive and exhaustive.

## Creating a Classification Application

Classification applications require the following fields:

1. An application name, e.g. 'Security Cam People Classifier'.
2. A list, output\_subjects, of subjects to classify the input media, e.g., 'security alert', ' employee', and 'visitor'.
3. An optional list, input\_subjects, of one or more subjects to store input media. It can be output subjects from other Cogniac applications.

To view additional, optional application creation fields and their default values, see [Applications - Create](/docs/applications-create).

Application Name

It is best practice to create applications with short but descriptive names that easily identify the end goal of the application to other users in the same tenant.

You can also view the entire flow on the Classification Creation → [[Here]](/docs/creating-a-classification-application).

## Classification Subjects and Feedback

Classification applications select a single output subject in each input media item. When providing application feedback, selecting the subject that appears most prominently or is best represented in the media item is best practice. To attain an accurate and stable application, continue to upload new media to the application's input subjects and provide feedback on the application's subject assertions. Monitor the application's model performance statistics: Precision, Recall, and F1 scores until sufficient accuracy is reached.

## Feedback Context

It is best practice to provide feedback in a manner that matches the feedback of a reasonable human expert in the application's domain. Providing highly contextual feedback for a classification application that will be used to process out-of-context images may result in lower model performance.
For example, while providing feedback to a classification application trained to identify if an image contains a particular person or subject, it is not recommended to provide positive feedback for blurry images or images where the individual providing feedback is aware the subject is in the image but is not visible without that knowledge.

The semantics of a classification application always require the selection of precisely one output subject. If, for some reason, there are media items presented to the application with none of the desired subjects or multiple of the desired subjects, an additional class or classes can be added to deal with these exceptional cases.

For example, if no subject of interest appears in some media items, an output subject representing 'None' or 'No Cats or Dogs' can be added. Similarly, if some media items contain multiple subjects, you can add a subject like "Multiple Cats or Dogs" to classify these images. This strategy works best if these cases are relatively rare. If you expect to have many images with no subjects or multiple subjects, then the 'Detection' application type is probably a better choice.

Note:

Because subjects are arbitrary and the classifier learns the semantics, combining the "none" exceptional subject and the "multiple" exceptional subject into a single subject is possible. For example, in a ****'cat versus dog'**** classifier with a cat subject and a dog subject, a third class, ****"cat dog exceptions"****, could be added to cover both exception cases of ****'no cats or dogs'**** and ****'multiple cats or dogs'****. The application will automatically learn to select this class whenever these conditions apply.

****Use an 'Exception Class' to handle problematic images****

Use an 'exception subject' in a classifier application to aggregate the relatively infrequent exceptional cases that often occur when none of the normal subjects are present in the media, multiple of the normal subjects are current, or the media is otherwise off-domain. Keep track of the subject semantics with the subject description field. If the 'no subject' or 'multiple subjects' cases are relatively frequent, then a Detection Full-frame application type may be more appropriate.

Because neural networks can quickly learn arbitrary functions, this technique above can be used for significant effect. For example, it is possible to have a classification app where there is a ****'cat'**** subject and a ****'cat with mouse in mouth'**** subject where, through consistent feedback, the application model learns that ****'cat with mouse in mouth'**** should always be prioritized over ****'cat'**** even though ****'cat with mouse in mouth'**** by definition contains a cat.
