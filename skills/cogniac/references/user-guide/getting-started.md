# Getting Started

## Overview

After creating an account, follow the steps to make your first application.

If you have not received an invite to your tenant, please send us an email at support@cogniac.ai

Gathering as many images as possible that showcase your defect/anomaly is essential. Usually, a couple of hundred is good to get started. We will need both good examples (no defects) and bad examples (defects).

## Step 1: Create A New Application

After logging into the web app, start by creating a new application. Our system defines applications as a "project" - a specific visual recognition task using a group of image or video sources.

Expand the Application Builder, and under the Vision AI Applications tab, select a type.

![](../../../assets/media/images/image%2845%29.png)

Enter the name of the application.

![](../../../assets/media/images/image%2846%29.png)

Next, select or create input subjects to add to your application. Input subjects are collections of related media that are meant to be processed by your application. You can add multiple input subjects to your application, and users generally segment inputs from different sources into different input subjects.

![](../../../assets/media/images/image%2847%29.png)

Add output subjects, the items, or conditions you plan to detect from within images or video. Note that you won't be able to add the output subject later.

![](../../../assets/media/images/image%2848%29.png)

You can skip editing “Application Type Configuration“ tab for now.

![](../../../assets/media/images/image%2849%29.png)

## Step 2: Add Images To Your Application

In this example, we'll upload a batch of images from our local disk.

![](../../../assets/media/images/image%2851%29.png)

Upload various images, some of which should contain the items of interest defined in your list of output subject tags.

![](../../../assets/media/images/image%2852%29.png)

## Step 3: Provide Feedback To Your Application

Every application requires labeled data to generate the image classification Machine learning model. The labeled data is created by providing human feedback on the images. Feedback is simply a process where the system presents the user with an image and a predicted subject\_tag and asks the user to verify that the subject tag is correct. If incorrect, the user can correct the prediction. Some applications can reuse existing labeled data in the system, but for this example, we will assume that there is no labeled data for your Application.

Wait a few minutes for the system to process the images you just uploaded. You should see the counter next to the "Pending Feedback" increase. Click on the button to start giving feedback. Many users upload batches of 100 images at a time, but it is possible to upload fewer or more images simultaneously.

![](../../../assets/media/images/image%2853%29.png)

This screen shows that the system detected a "fork" in this image. This is correct, and it's simple to 'submit' your feedback for confirmation. You can continue providing feedback until you complete the current queue of images.

[![](../../../assets/media/images/bwfuma8udumok75uj5xggpng.png)](../../../assets/media/images/bwfuma8udumok75uj5xggpng.png)

After giving feedback on a few dozen images, your application should start performing better. Click on the detections tab to see recent detections and the confidence level. Note: Just after creating your application, some detections are expected to be wrong. The system will learn over time as you upload more images and give feedback.

## How Much Feedback Is Required?

You should generally start to see "better than random" results after a few dozen 'consensus' training images per subject. The performance of your application will initially increase dramatically as more feedback is provided and more consensus items are generated as training data. Beyond 500-1000 consensus images for a given subject, the application performance will continue to increase slowly. Different media sources and different subject types require different amounts of consensus data to achieve a given performance level. The more the appearance of your subjects naturally varies in your input images, the more consensus data you will need. You can track the performance of your Application in the web app. If the performance is unsatisfactory, you can continue adding additional training images and provide more feedback to boost the performance.
