# Deployments Quickstart Guide

Deployments are a new feature of the Cogniac CloudCore and EdgeFlow systems that provide extended control over production visual inspection pipeline workloads. Deployment Groups and Deployment Workflows are created and managed via the Cogniac CloudCore platform and executed on Cogniac EdgeFlow physical appliances or Cogniac CloudFlow instances.

The Deployments feature provides the following benefits to Cogniac users:

- Further decouples CloudCore visual application development from EdgeFlow application deployment which allows each to progress with minimal dependencies
- Provide fine-grained control (when required) over all application model versions and application configurations
- Supports application pipelines “rerouting” in Deployment Workflows, allowing for different application assemblies than in CloudCore
- Enable perfectly repeatable execution of frozen application pipelines in the form of immutable Deployment Workflows
- Manage identical fleets of EdgeFlow devices as a single virtual entity in the form of a Deployment Group

The Deployments feature is powerful as it introduces new higher level abstractions for managing production or testing environments. Two new high level management concepts are introduced, the Deployment Group and the Deployment Workflow.

The following diagram demonstrates the relationship between the new managed objects introduced by the Deployments feature:

![](/assets/media/images/deployments-quickstart-guide-image-1bzjvit5.png)

The definitions of the core high-level concepts are as follows:

| Concept | Definition |
|---------|-----------|
| **EdgeFlow** | A dedicated inference resource in the form of a physical EdgeFlow appliance or a CloudFlow instance |
| **Deployment Group** | A set of similar purpose and capacity EdgeFlow instances |
| **Deployment Workflow** | A “frozen” application pipeline including models and configuration intended for execution across a Deployment Group |

## EdgeFlow

In this context EdgeFlow represents an EdgeFlow appliance, or a CloudFlow instance, since CloudFlow is effectively a type of EdgeFlow. EdgeFlow instances are an already familiar feature of the Cogniac System, accessible from the “EdgeFlow Gateways” menu item, where individual EdgeFlow instances can be managed via a view shown here:

![](/assets/media/images/deployments-quickstart-guide-image-kzsgnqt2.png)

## Deployment Group

The Deployment Groups concept allows groups of similar EdgeFlow instances to be grouped together so that they can be more easily managed as a group. Most importantly, a Deployment Group enables a specific Deployment Workflow to be deployed across a set of identical EdgeFlows in a simplified manner. An individual Deployment Group can execute a single Workflow at a time.

The list of configured Deployment Groups can be viewed from the Deployment Groups Menu item in CloudCore:

A list of Deployment Groups will appear as follows, which allows selection of existing Deployment Groups as well as the creation of new Groups:

![](/assets/media/images/deployments-quickstart-guide-image-ujpx10e0.png)

Individual Deployment Groups present a view somewhat similar to the individual EdgeFlow View.

![](/assets/media/images/deployments-quickstart-guide-image-1qv69j83.png)

The essential characteristics of a Deployment Group are as follows:

- A set of EdgeFlows all of the same model type
- The current Workflow that is assigned to the deployment group
- Update Workflow from a list of available workflow with matching Edgeflow model
- Pre-load Workflow from a list of available workflow with matching Edgeflow model so workflow can be downloaded in the background without impacting production workflow
- A set of Managers who have permission to change a specific Deployment Group
- Deployments History shows the history of the workflows deployed to this group
- Delete Group where user can delete unused deployment groups

EdgeFlow instances can be assigned to a Deployment Group either via this Deployment Group view or via the original EdgeFlow view. Here is how the assignment looks from the original EdgeFlow view:

![](/assets/media/images/deployments-quickstart-guide-image-ywdfwhu0.png)

> **One key aspect of Deployments is that they replace the previous “Model Deployment Policy” mechanism.** Previous staging and production model deployment policy configurations can be easily migrated to Deployments along with the corresponding per-app model configuration.

Please contact Cogniac Support for assistance in programmatically migrating your previous staging and production configurations to Deployment Groups and Deployment Workflows.

## Deployment Workflow

Deployment Workflows (or “Workflows” for short) are a “frozen” application pipeline including models and config intended for execution across a Deployment Group.

An essential characteristic of Workflows is that they are immutable, by design. Once created, a Workflow can never change. This ensures that a particular workflow produces consistent results when deployed on different EdgeFlow instances and especially over time. This characteristic enables high-confidence rollback and as such lowers the bar to making forward progress.

Workflows are assigned to a Deployment Group from the Deployment Group view, as shown here:

![](/assets/media/images/deployments-quickstart-guide-image-zmtufh00.png)

The act of assigning a current Workflow to a deployment group results in the immediate provisioning of all applications and configuration associated with the Workflow on all EdgeFlow instances in the Deployment Group.

## Workflow Creation

Deployment Workflows can be created in CloudCore via the Deployment Workflows Menu item:
![](/assets/media/images/deployments-quickstart-guide-image-ulbg6ol8.png)

Once the Deployment Workflows menu is selected, you can create new workflows and see a list of existing workflows.

![](/assets/media/images/deployments-quickstart-guide-image-tjaq2fd3.png)

Click on the blue plus button to create a new workflow:

![](/assets/media/images/deployments-quickstart-guide-image-d5bnnlc1.png)

Enter the Name of the Workflow, Description and select the targeted EdgeFlow/CloudFlow type from the drop down menu. Then you can select the subset of the applications to be included in the workflow.

![](/assets/media/images/deployments-quickstart-guide-image-ar7ozodl.png)

If you need to change the configuration of the applications for this workflow, you can hover over the application and click on the edit icon on the right corner of the application. A detailed configuration panel is displayed when you click on the edit icon:

![](/assets/media/images/deployments-quickstart-guide-image-byf4un03.png)

![](/assets/media/images/deployments-quickstart-guide-image-0nglxq7k.png)

You can make modifications on the application configuration and save the configuration. These changes only affect the workflow you are creating, not the CloudCore configuration.

Detailed information about inference execution policies are available at
https://cogniac.readme.io/docs/applications

If there are many applications in view, you can click into full screen mode and Deselect All and select only the desired applications to be included in the Workflow.

Once done, click Create Workflow. The newly created workflow will be displayed.

![](/assets/media/images/deployments-quickstart-guide-image-ru7hvbsi.png)

Click on the pipeline icon next to Applications would bring you the pipeline view of the workflow in a separate tab in the browser:

![](/assets/media/images/deployments-quickstart-guide-image-y1pa90ax.png)

## Workflow Clone

You can also clone existing workflows in CloudCore. Open up an existing workflow, click on Clone Workflow button.

![](/assets/media/images/deployments-quickstart-guide-image-vbyfodv5.png)

You can modify the Name, Description, Retarget the Edgeflow model, and add, remove or edit the applications to the previous existing workflow. After you are done with the modification, click Save New Workflow. You will be brought to the view of the new workflow you have cloned.
