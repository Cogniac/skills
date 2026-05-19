# CloudCore Overview

## Cogniac CloudCore System Concepts

The Cogniac {{glossary.CloudCore}} system is a powerful tool that utilizes Deep Learning to automate visual observation tasks, including classifying, detecting, counting, locating, and measuring objects, actions, or conditions in images or videos.

## ****Media****

Media refers to still images or videos. It can be uploaded into the Cogniac system through various methods, including the API, web application or EdgeFlow gateway systems. Additionally, the Cogniac system has the ability to actively acquire media from external sources, such as network cameras or machine vision cameras.

## ****Applications****

An application is a unit of work that performs a single visual task. The Cogniac system supports various application types, including classification, detection, measurement, localization, and counting. Many of these applications are based on deep convolutional neural network models that have been trained to perform specific tasks.

## ****Subjects****

A subject is a user-defined concept that helps to group, manage, and route media within the Cogniac system. Subjects are usually aligned with the objectives of the visual observation tasks being automated. For instance, a subject could be "defective gears" or "cats with a mouse in their mouth."

## ****Data Flow****

Media is processed within the Cogniac system through subjects and applications. The basic process involves uploading media into an input subject, which is then processed by an application. The application associates the media with an output subject, which can serve as input for another application. This structure enables the creation of complex processing pipelines.

![](../../../assets/media/images/i8foc6hezeg9hbvlofbpuqpng.png)

For more information on specific application workflows, please refer to the [Cogniac Applications documentation](/docs/application-types).

## ****Data Security****

Cogniac prioritizes {{[glossary.Data](http://glossary.Data) Security}} and adheres to industry best practices to safeguard your information. We implement a private tenant architecture model, which means that each customer's data is completely separated and isolated from that of other customers. This guarantees that only the users you invite to your tenant can access your media, subjects, applications, and related data.

![](../../../assets/media/images/5dc2wdik4iqyxnhj5qpng.png)

## ****Quick Setup****

Users can create tenants and virtual workspaces to store and manage media and applications. They can invite other users to join the tenant after its creation. Once the tenant is established, users can proceed to create their first application.

> Note:
>
> For information on applications, view this tutorial: [Getting Started: Applications](https://ior.ad/9J2b) For information on subjects, view the tutorial: [Getting Started: Subjects](https://ior.ad/9N97)

## ****Application Training****

Upload media to the application by either selecting an input subject or capturing it from a live stream. Provide feedback on the media to help train the application to automatically detect, measure, or count the items of interest.

## ****Detect Items or Conditions of Interest****

The application generates detections as media is uploaded or captured from the input subjects. These detections can be automated or human-generated and are created from items of interest within the user's visual media.
