# Cogniac Subjects

## Subject

A subject is the primary method through which media is organized and managed within the Cogniac system. Subjects are defined by the users of the system and can be quite arbitrary. They are generally related to the objectives of the visual observation task being automated. At its simplest, a subject can be thought of as a ‘tag’ associated with an image. More broadly, ****a subject represents any user-defined concept that can be connected to the content or domain of a group of images or video****s. Subjects can be straightforward concepts, such as “cat,” or they can convey more complex information, such as “cat with mouse in mouth.” A subject can also define the “domain” of an image generation process, like “cat door camera,” or any logical grouping of related images.

## Subjects such as Application Inputs and Outputs

Media flows through applications using Cogniac subjects. Subjects define both the input and output of these applications. It is beneficial to create subjects with specific names to avoid confusion with subjects used by other users within the same tenant.

For example, "lobby security camera feed" is an appropriate subject name for videos or images captured from a security camera. However, subject names need to be unique. Concise and helpful output subject names for a security camera classification application include "security alert," "visitor," and "employee." These names are suitable for use during Application Training.

> Subject UID
>
> Subject names do not need to be unique within the Cogniac System. When a subject is created, a unique Subject UID is assigned to identify that subject throughout the system.
>
> Unique Subject UIDs allow:
>
> 1. Subject names and metadata can be edited without affecting any existing associations between subjects and media.
> 2. Multiple subjects can share the same name while referring to different items of interest, without mixing up subject-media associations among them.

## Subject-Media Associations

The primary function of a Cogniac application is to create associations between media items and Cogniac subjects, effectively labeling the media with the appropriate subject.

- The strength of the association between a subject and a media item is determined by the likelihood that the subject is related to that media. Association probabilities close to 1.0 indicate a very strong positive association; for example, "this image contains a cat." Conversely, probabilities close to 0.0 indicate a very strong negative association; for instance, "this image does not contain a cat."
- Applications that utilize deep convolutional neural networks are designed to route images from the input subjects to the correct output subjects with an appropriate probability. Like all systems, this learning process relies on accurately labeled example images. Application users provide feedback to the Cogniac system regarding previous model predictions. This feedback helps the system establish consensus associations between subject media, which is the foundation of the model training.
- The Cogniac system calibrates both application models and user feedback and automatically assesses their accuracy. An application's predictions become stronger as its model accuracy improves based on accurate user feedback.
- Subject-media associations can be established by directly uploading media to a subject, which creates a strong and authoritative link between the subject and the media. This method is typically used to input media into the system for processing by associating it with an input subject.

  Alternatively, when media is uploaded directly to an output subject, it essentially labels the media with that subject for training purposes. However, caution is necessary when linking media directly to output subjects, as this process bypasses the feedback consensus system that usually ensures the accuracy of consensus labels associated with output subjects.
