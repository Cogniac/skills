# Cogniac Rare Subject Mining Best Practices

## Best Practices for Rare Subject Mining

Cogniac Confidential

During the application building stage, the Cogniac system is designed to help discover and label rare Subjects to enhance Model accuracy as quickly as possible. We refer to this process as “rare subject mining.” This technical note outlines our best practices for implementing this process.

## Starting assumptions:

- You have several images labeled for the rare condition, with some instances in the training set and others in the validation set for both True and False Consensus.
- A model has been released with a validation F1 of greater than 0%

Set the detection threshold for the rare subject below the default value of 0.5. A recommended threshold range is between 0.2 and 0.3.

![](../../../assets/media/images/image%2865%29.png)

## Iterate on the following process:

1. Replay or process a large set of random media, ranging from thousands to tens of thousands, through the app, typically using an Input Subject.
2. Wait until the Replay has finished completely (no more outputs will appear in the application output view).
3. Optionally, check for rare subject candidates from the Subject Media view using the following filter configuration:

![](../../../assets/media/images/cogniac-rare-subject-mining-best-practices-image-ikd306nw.png)

****Note the lower probability above 0 and the sort specified on “Highest Prob first”.****

- Perform “Replay” :

  ![](../../../assets/media/images/image%2869%29.png)

- Select the reply to use the rare subject you are mining. Ensure that the lower end of the probability filter is set above 0, and Force Feedback is selected.

![](../../../assets/media/images/image%2871%29.png)

1. Please give your feedback using the yellow "Provide Feedback" button after the replay has finished.
2. Please wait for the release of a new model.
3. Repeat

If insufficient candidate media are identified during the iterative process, a more manual labeling approach will be necessary. This may involve manually searching through numerous images and providing feedback on specific items until the model successfully learns the subject. Alternatively, setting a progressively lower detection threshold might help reveal useful candidates.
