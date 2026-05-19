# Workflow Update

## Overview

This document is in addition to the Workflow Creation and Deployment document. You can also view this tutorial outlining the steps written in the following document:

## How to update an existing Workflow?

After creating a Workflow, it can be found in the ‘Deployment Workflows’ section. Refer to the screenshot below:
![](../../../assets/media/images/workflow-update-image-z33sd27y.png)

Users should navigate to the Workflows page, expand, and select the Workflow they wish to update.

![](../../../assets/media/images/workflow-update-image-1pbbwlz8.png)

At the bottom of the page, there is a button labeled "Workflow Update." By selecting it, users can update the following workflow parameters:

![](../../../assets/media/images/workflow-update-image-ybis062s.png)

- Auto Version Update -> Active / Inactive. This option enables users to deploy the latest version when there is a Workflow Update, such as adding or removing Applications.
- Name and Description are parameters that can be updated at any time.
- Once a Workflow is created, the EdgeFlow version cannot be updated.
- ****Applications - Add/Remove**** - To add an application, users should enter either the Application Name or the Application ID. The Application ID is a unique identifier that helps users filter to find the exact application, especially when there are many applications with the same name.

Users can choose the Pipeline View to display the Applications included in the Workflow.

![](../../../assets/media/images/workflow-update-image-lmxkr6zk.png)

After users have finished adding or removing apps, or updating the Workflow, they should click the Save Changes button to generate the latest version of the Workflow.

![](../../../assets/media/images/workflow-update-image-yv8u1ei1.png)

When a new model is released, a new workflow version will also be pushed. If Auto Version Update is enabled, the latest workflow version will automatically deploy with the latest model release.
