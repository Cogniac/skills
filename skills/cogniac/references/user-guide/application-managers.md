# Application Managers

## Overview

When a user creates a new application, it is assumed that they are the Subject Matter Expert for the specific application type and the data being set up. Cogniac refers to this individual as the Application Manager, a role that comes with certain privileges. The Application Manager is responsible for configuring the application, which includes managing all settings and gathering feedback. Other users within the organization can view the application and provide feedback, but the Application Manager, until additional Application Managers are appointed, holds the responsibility for confirming feedback and managing the settings.

Users within the tenant will provide feedback on images to assist with data labeling; however, they cannot initially reach a consensus on their own. Since achieving consensus is crucial for training the model to understand the ground truth, the Application Manager will serve as the final authority for labeling items as consensus until a user has proven sufficient accuracy.

Users are not able to drive images to consensus through feedback. Instead, items will be forwarded to the Application Manager's feedback queue. Initially, when new users are added, the Application Manager will have an increased responsibility for confirming feedback. However, as users build a history, this responsibility will decrease. Labeling images is essential for the system's accuracy, so it is important to rely on verification from a trusted source.

## Application Manager Setup

When a new application is created, the user who creates it becomes the default Application Manager.

![](../../../assets/media/images/image%2873%29.png)

To add more users to the Application Managers list, navigate to the Application Settings and scroll down to the bottom.

![](../../../assets/media/images/image%2855%29.png)

Choose the users you would like to designate as Application Managers.

##

![](../../../assets/media/images/image%2856%29.png)

## Future

The aim is to ensure accuracy in the labeling process and to establish a continuous assessment of user feedback to avoid repetitive comments. Evaluating the feedback will help identify labeling errors and address them from a hierarchical perspective.
