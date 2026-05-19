# Cogniac Best Practices Iron Fist

## Best Practices for Improving Applications:

The “Iron Fist” Technique

****Cogniac Confidential****

- Once you have an application in the Cogniac system with over 100 labeled media, you should begin to see models released with an assessed accuracy in the 90% range or higher, depending on the complexity of the visual task.
- If you have a large dataset, you can extract the most challenging images to push the model to learn more effectively. This technique, known asLabeling, focuses on compelling the model to learn from the hardest examples. We refer to this approach as the "Iron Fist" technique.
- This technique is based on the idea that, at any given moment, the most challenging images for a model are the ones for which its predictions are the most incorrect. These images are also the most valuable to label, as they push the model to learn more effectively.

The technique is as follows. After a new model is released:

****1. Replay ALL (or up to 1000 RANDOM) images from the input subject****

To find the rarest and most challenging images, it is important to draw from the largest possible sample pool. The system will automatically disregard media that has already been labeled in your target application. The main goal of this step is to update the model's predictions based on the current best model available. This is essential for identifying the "worst-of-the-worst" predictions from the current best model when evaluated against the largest dataset possible.

****2. Wait for the replay to complete****

Monitor the output subject (with the probability filter set to the full range of 0 to 1) and refresh until no new output items appear.

****3. Prepare to replay again the most difficult items by selecting a probability range for the most difficult samples in a single subject****

For instance, when determining an ROI in preparation for a subsequent inspection, and when most images are expected to contain the ROI, select a probability range from 0 to approximately 0.5, which encompasses the 'most incorrect' predictions.

In situations where the ROI is not consistently present, the range considered to be ‘most incorrect’ might be closer to approximately [0.4, 0.6]. Examine the output related to your subject of interest and adjust the probability range accordingly to visually assess the results of selecting a specific probability range.

In OCR applications, images with the lowest probabilities tend to be the most challenging samples.

****4. Replay from your application from a single output subject with a probability filter selected to contain the ‘most wrong’ outputs.****

Set up the replay to handle between ****25 and 50 images, and enable force feedback****.

****5. Wait for the replay to complete.****

If you have many items in the output subject, it may take some time to process.

****6. Provide feedback on the “most wrong” images from the feedback queue.****

Exert strong control over the model using your "Iron Fist"!

****7. Wait for a new model to be released and repeat.****

> ****Important Note:****
>
> When utilizing the Iron Fist technique (or any labeling strategy that emphasizes more challenging images), the application accuracy reported by the Cogniac system will be****much lower than the actual real-world application accuracy****. Because the application is assessed on a random subset of the labeled images, you are effectively making the application test much more difficult than ‘real-life’ by labeling mostly the hard images. This is good because the more difficult training and validation set forces the model to “train harder”. As a result, it will perform better in the “real world” than the application accuracy indicates.
