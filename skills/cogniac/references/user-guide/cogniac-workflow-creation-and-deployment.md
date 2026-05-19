# Cogniac Workflow Creation and Workflow Deployment

## 1. Objective

This document explains how to use deployment groups and deployment workflow (also called workflow), and how to create them using the steps below.

## 2. Overview

Deployment provides extended control over production visual inspection pipeline workloads. Deployment Groups and Deployment Workflows are created and managed via the Cogniac CloudCore platform and executed on Cogniac EdgeFlow physical appliances or Cogniac CloudFlow instances.

## 3. Introduction

The Deployments feature provides the following benefits to Cogniac users:

- Decouples CloudCore visual application development from EdgeFlow application deployment, which allows each to progress with minimal dependencies
- Provides fine-grained control (when required) of overall application model versions and application configurations
- Supports application pipelines “rerouting” in Deployment Workflows, allowing for different application assemblies than in CloudCore
- Enable perfectly repeatable execution of frozen application pipelines in the form of immutable Deployment Workflows
- Manage identical fleets of EdgeFlow devices as a single virtual entity in the form of a Deployment Group

The Deployments feature is powerful as it introduces new, higher-level abstractions for managing production or testing environments. Two new high-level management concepts are introduced: the Deployment Group and the Deployment Workflow.

The following diagram demonstrates the relationship between the new managed objects introduced by the Deployments feature:

![](../../../assets/media/images/image%28130%29.png)

## 4. Main terminology used in this document

The definitions of the core high-level concepts are as follows:

- EdgeFlow - a dedicated inference resource in the form of a physical
- EdgeFlow appliance or a CloudFlow instance
- Deployment Group - a set of similar-purpose and capacity EdgeFlow instances
- Deployment Workflow - a “frozen” application pipeline including models and configuration intended for execution across a Deployment Group

##

## 5. EdgeFlow

In this context, EdgeFlow represents an EdgeFlow appliance or a CloudFlow instance since CloudFlow is effectively a type of EdgeFlow. EdgeFlow instances are an already familiar feature of the Cogniac System, accessible from the “EdgeFlow Gateways” menu item, where individual EdgeFlow instances can be managed via a view shown here:

![](../../../assets/media/images/image%2878%29.png)

## 6. Deployment Group

The Deployment Groups concept allows groups of similar EdgeFlow instances to be grouped to be more easily managed as a group. Most importantly, a Deployment Group enables a specific Deployment Workflow to be deployed across a set of identical EdgeFlows in a simplified manner. An individual Deployment Group can execute a single Workflow at a time.

To create a deployment group, click on the “+” sign, enter the name and description(optional), then click on “Okay”.

![](../../../assets/media/images/image%2882%29.png)

The list of configured Deployment Groups can be viewed from the Deployment Groups Menu item in CloudCore.

![](../../../assets/media/images/image%2879%29.png)

A list of Deployment Groups will appear as follows, which allows the selection of existing Deployment Groups as well as the creation of new ones.

Individual Deployment Groups present a view somewhat similar to the individual EdgeFlow View.

![](../../../assets/media/images/image%2880%29.png)

![](../../../assets/media/images/image%2881%29.png)

The essential characteristics of a Deployment Group are as follows:

- A set of EdgeFlows, all of the same model type
- The current Workflow that matches the deployment group under the Target Workflow
- Update Workflow from a list of available workflows with a matching EdgeFlow model
- Preload the workflow onto the EdgeFlow before switching over to the new workflow. This will minimize downtime.
- A set of Managers who have permission to change a specific Deployment Group
- Deployments History shows the history of the workflows deployed to this group
- Delete Group, where the user can delete unused deployment groups

EdgeFlow instances can be assigned to a Deployment Group either via this Deployment Group view or the original EdgeFlow view. Here is how the assignment looks from the original EdgeFlow view:

![](../../../assets/media/images/image%2884%29.png)

One key aspect of Deployments is replacing the previous “Model Deployment Policy” mechanism. Previous staging and production model deployment policy configurations can be easily migrated to Deployments and the corresponding per-app model configuration.

Please contact Cogniac Support to programmatically migrate your previous staging and production configurations to Deployment Groups and Deployment Workflows.

You can also check the tutorial below:

<iframe src="https://www.iorad.com/player/2328496/Cogniac---How-to-create-a-Deployment-Group?src=iframe&oembed=1" width="100%" height="500px" style="width:100%;height:500px;border:none;" allowfullscreen></iframe>

## 7. Workflow

Deployment Workflows (or “Workflows” for short) are a “frozen” application pipeline including models and config intended for execution across a Deployment Group.

An essential characteristic of a Workflow is that it is immutable by design. Once created, a Workflow can never change. This ensures that a particular workflow produces consistent results when deployed on different EdgeFlow instances, especially over time. This characteristic enables high-confidence rollback and, as such, lowers the bar to making forward progress.

## 7.1 Workflow Creation

Deployment Workflows can be created in CloudCore via the EdgeFlow Menu item:

![](../../../assets/media/images/image%2885%29.png)

Once the Deployment Workflows menu is selected, you can create a new workflow and see a list of existing Deployment Workflows.

![](../../../assets/media/images/image%2886%29.png)

Click on the blue “plus” button to create a new workflow:

Enter the Name of the Workflow, Description (add an optional description e.g., purpose of the Workflow), and select the targeted EdgeFlow/CloudFlow type from the drop-down menu. You can select the Auto Version Update, which will create a new version if there is a model update, an application-specific change, or a camera update for the applications in a Workflow. Lastly, you can select the applications to add(you need to click first on “Deselect All” because it is selected by default) to the Workflow and click the blue Create Workflow button.

![](../../../assets/media/images/image%2887%29.png)

![](../../../assets/media/images/image%2888%29.png)

Suppose you need to change the configuration of the applications for this workflow. In that case, you can hover over the application and click on the edit icon in the right corner of the application. A detailed configuration panel is displayed when you click on the Edit icon:

![](../../../assets/media/images/image%2889%29.png)

Once they click on the Edit icon, a view similar to this should be visible:

![](../../../assets/media/images/image%2890%29.png)

![](../../../assets/media/images/image%2892%29.png)

Users can make modifications to the application configuration and save the configuration. These changes only affect the workflow they are creating, not the CloudCore configuration.

Detailed information about inference execution policies is available at [Applications](/docs/applications).

If many applications are in view, you can click into full-screen mode, deselect all, and select only the desired applications to be included in the Workflow.

Once done, click Create Workflow. The newly created workflow will be displayed similarly to the image below:

![](../../../assets/media/images/image%2893%29.png)

Click on the pipeline icon next to Applications will bring you the pipeline view of the workflow in a separate tab in the browser:

![](../../../assets/media/images/image%2894%29.png)

![](../../../assets/media/images/image%2895%29.png)

## 7.2 Workflow Clone

You can also clone existing workflows in CloudCore. Open up an existing workflow, and click on the “Clone New Workflow button”.

![](../../../assets/media/images/image%2896%29.png)

![](../../../assets/media/images/image%2897%29.png)

Users can modify the Name, Description, and Retarget the Edge Flow model and add, remove, or edit the applications to the previous existing workflow. After you are done with the modification, click Save New Workflow. They would be brought back to the view of the new workflow you have cloned.

You can also check the tutorial below:

<iframe src="https://www.iorad.com/player/2336788/Cogniac---How-to-create-a-WorkFlow?src=iframe&oembed=1" width="100%" height="500px" style="width:100%;height:500px;border:none;" allowfullscreen></iframe>

## 7.3 Workflow Update

Once a Workflow is created, it can be accessed from the section Deployment Workflows. Please see the screenshot below:
![](../../../assets/media/images/workflow-update-image-z33sd27y.png)

Once the users are navigated to the Workflows page, they should expand and select the Workflow they need to update.

![](../../../assets/media/images/workflow-update-image-1pbbwlz8.png)

At the bottom of the page, there is a button called Workflow Update, and by selecting it, users can update the following Workflow parameters:

![](../../../assets/media/images/workflow-update-image-ybis062s.png)

- Auto Version Update -> Active / Inactive - this option allows the user to deploy the latest version once there is a Workflow Update (When the User adds or removes Applications )
- Name / Description - are parameters that can be updated anytime
- EdgeFlow version can’t be updated once the Workflow is created.
- Applications - Add/ Remove - To add an application Users should type either an Application Name or Application ID (Application ID is a unique identifier and allows the users to filter the exact application if there are many applications with the same name)

Users can select the Pipeline View that will expand the Applications included in the following Workflow.

![](../../../assets/media/images/workflow-update-image-lmxkr6zk.png)

Once the user has finished adding/removing apps or updating the Workflow, they should click on the Save Changes button in order to generate the latest version of the Workflow.

![](../../../assets/media/images/workflow-update-image-yv8u1ei1.png)

Once a new Model is released, this also pushes a new Workflow version. If the Auto Version Update is enabled, the latest Workflow version will be automatically deployed with the latest model release.

You can also view the Update Workflow tutorial → [Here](https://ior.ad/agv5)

## 8. Deploying a Workflow to the EdgeFlow

Once the Workflow is created, it can be assigned to a deployment group. A deployment group without a workflow is considered undefined.

When a Deployment Group is selected, the user can define when the workflow is deployed to the EdgeFlows linked to that group by using one of the two options available under the ****Target Workflow**** tab: ****Change Scheduled Workflow**** or ****Deploy Now****.

The Target Workflow holds details about the intended workflow. If the workflow currently deployed on an EdgeFlow differs from the targeted workflow, an informational message is displayed to alert the user.

![](../../../assets/media/images/image%28279%29.png)

![](../../../assets/media/images/image%28292%29.png)

## 8.1 Change Scheduled Workflow

It allows the user to choose between two options:

“Periodically deploy the latest version”.
and
“Deploy a specific version one time”.

## 8.1.1 Periodically deploy the latest version

This feature allows the user to keep their application up to date with the latest version and trigger a deployment if EdgeFlow doesn’t have the latest version deployed. Users can choose the frequency to check for a newer version when this option is selected. Below are all the frequency options available:

- When a new version is created, and the auto version is active, it periodically checks for a more recent version and deploys the latest version hourly.
- Daily - checks on a specific day of the month (1 to 30) and specific time (00 to 23h) and minutes in 15-minute intervals (00,15,30,45)
- Weekly - is checking on a specific day/s (if multiple selections) of the week (Monday to Friday) and specific time (00 to 23h) and minutes in 15-minute intervals (00,15,30,45)

Please see the options displayed in the images below:

![](../../../assets/media/images/image%28123%29.png)

![](../../../assets/media/images/image%28122%29.png)

![](../../../assets/media/images/image%28124%29.png)

![](../../../assets/media/images/image%28125%29.png)

## 8.1.2 Deploy a specific version one time

Allows the user to select a date and time (for the deployment) from the Calendar. After choosing the Workflow version, date, and time of deployment, click “Finish”.

![](../../../assets/media/images/image%28118%29.png)

The scheduled Workflow will be displayed in the Target Workflow section, and under it, you will see the date and time that you have planned for the deployment to start.

![](../../../assets/media/images/image%28291%29.png)

##

- The Workflow will be displayed in the 'Workflow Deploying Now' section until the deployment is complete.

![](../../../assets/media/images/image%28284%29.png)

- Once the deployment is successful, it will be displayed in the Target Workflow section.

![](../../../assets/media/images/image%28285%29.png)

## 8.2 Pre-load Workflow

The user can select the ‘Pre-load Workflow software on Deployment Group EdgeFlows’, which should trigger a deployment before the actual deployment on the EdgeFlow.

Select the Workflow that you want to be pre-loaded.

![](../../../assets/media/images/image%28128%29.png)

After it is pre-loaded, it will move to the Pre-loaded Workflow section.

![](../../../assets/media/images/image%28129%29.png)

You can also check the tutorial below:

<iframe src="https://www.iorad.com/player/2340976/Cogniac---How-to-deploy-Workflow-to-the-EdgeFlow?src=iframe&oembed=1" width="100%" height="500px" style="width:100%;height:500px;border:none;" allowfullscreen></iframe>

## 9. Check the deployment

Each workflow has a unique ID, which helps us identify a specific Workflow deployment in the logs. The deployment workflow consists of four stages (statuses) in the Edge Flow, and all of the stages should be checked to confirm whether the deployment was successful.

Below are the four statuses that exist under the ‘deployment\_status’ in the Deployments History:

- ****Download**** - Downloads the workflow json (checks for md5)
- ****Delete****- Deletes existing pods currently deployed in the EdgeFlow
- ****Deploy**** - Deploys the downloaded json file from the CloudCore to the EdgeFlow
- ****Success**** - This is the final status, indicating the deployment was successful

Also, we need to be sure if all of those have the correct http status code (200 for Success) displayed under the ‘get\_workflow\_status\_code’.

## 9.1 View the deployment history

There are two ways to check a deployment workflow in the system. The first is by navigating to the deployments history in the Deployment Group tab. However, this option does not give a complete detailed log, so we must also check the Edge Flow logs during the specified time and for the set (ID: Version) combination.

![](../../../assets/media/images/image%28104%29.png)

Once the user has collected the information from the Deployments History in the Deployment Group tab, they will need to navigate to the Edge Flow device using the Edge Flow menu item at the top of the page.

![](../../../assets/media/images/image%28105%29.png)

After that, select the EdgeFlow device from the list of devices available:

![](../../../assets/media/images/image%28106%29.png)

Then, the Status page of the Edge Flow device will be opened. On this page, you can find a lot of helpful information about the device, such as GPU memory usage, Temperature, CPU and Memory usage, and Network statistics.

On the top of the page, there are also two buttons, Status and Workload Status, and the user needs to select the Status button.

![](../../../assets/media/images/image%28115%29.png)

Once the Status of the Edge Flow is selected, a new page will be opened in the same browser window. It should look like the one below:

![](../../../assets/media/images/image%28109%29.png)

After selecting the deployment option, we need to narrow down the timespan by selecting the Calendar field in the top right corner and clicking “Submit”.

![](../../../assets/media/images/image%28110%29.png)

The deployment logs should be visible in reverse chronological order for the user, and they need to expand each log to view the full details inside it.

We already have the ID and version from the previous screen (LTAVG:0), and we can use the Ctrl+F (to find on the page) and check if this is the same Workflow ID.

Now, we can see the logs have the same ID and confirm the deployment steps (stages) are completed.

![](../../../assets/media/images/image%28111%29.png)

![](../../../assets/media/images/image%28112%29.png)

We see the sequence goes as follows (from the bottom to the top):

- "deployment\_status": "downloading workflow"
- "deployment\_status": "downloaded workflow"
- "deployment\_status": "deleting existing workflow"
- "deployment\_status": "deploying workflow"
- "deployment\_status": "success"

Thus, our deployment was successful. However, we also need to check the Pods, and we can do it by going back to the EdgeFlow device status page and selecting Workload Status. If all the pods (Application pipelines) are green, then the EF device deployment has succeeded.

![](../../../assets/media/images/image%28116%29.png)

The current workflow has only one Application with ID:a383truv. And once we check the Workload Status, we can see it is green:

![](../../../assets/media/images/image%28117%29.png)
