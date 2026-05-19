# Release Notes — 2025

## February 5, 2025

### Improvement: the ‘Current Workflow’ was updated to ‘Target Workflow’.

The ‘Current Workflow’ label has been renamed to ‘Target Workflow’ to improve clarity and better reflect its purpose within the deployment flow.

#### What’s improved:

- Clearer identification of the workflow that will be deployed.
- Reduced confusion between the active, target, and future configuration.
- Improved overall usability when managing deployments.
- Notifies the user if the deployed workflow differs from the targeted workflow.

![](../../../assets/media/images/image%28283%29.png)

This update helps users more easily understand which workflow is selected as the deployment target.

You can check the entire document → [Here.](/docs/cogniac-workflow-creation-and-deployment)

## October 30, 2025

### New Feature: Pixel Measurement tool

Added a Pixel Measurement Tool to the feedback queue for easy line and angle measurements directly on images — improving accuracy in pixel-sensitive projects. Currently, the Pixel Measurement Tool is only available for SAM.

![](../../../assets/media/images/image%28246%29.png)

You can review the changes in this document: [here](/docs/pixel-measurement-tool)

## October 7, 2025

### New Feature: Associate Media with a Subject

You can now ****associate any media item with a subject**** directly in the web app.

- Save important media for later use, even before the pipeline is ready.
- Organize media inside the platform instead of tracking in spreadsheets.
- Works with ****any subject**** — no pipeline restrictions.
- Clear confirmation message after each association.

![](../../../assets/media/images/image%28236%29.png)

This makes it easier to collect and manage “media of interest” today, so it’s ready for labeling or testing tomorrow.

You can review the entire document → [here](/docs/associate-media-with-subject).

## September 2, 2025

1. ### ****Improvement: Users are able to see AI and Non-AI applications listed in the Applications Summary.****

In ****Production Webapp****, the ****Applications Summary**** did not include ****Non-AI apps****. This limited visibility of the complete list of applications.

****Resolution:****

- ****Non-AI apps**** are now included in the Applications Summary list.

****Outcome:****
Users now get a ****complete and flexible view**** of all applications (AI + Non-AI applications) directly from the Webapp’s Applications Summary.

2. ****Improvement: Improved Error handling in the Integration App UI****

- Fixed the handling of cases where `build_id` is ****n/a****.
- Users can now create a new Integration App without having build\_id

![](../../../assets/media/images/123%281%29.png)

3. ## ****Improvement: Centralized TLS Certificate Management****

- TLS certificates for ****EdgeFlow****are now managed at the ****Tenant level****
- A single certificate update applies across all EdgeFlows in the tenant.
- Simplifies administration and reduces redundancy.
- Ensures consistent and reliable security management.
- Tenant Admin is the only user role that can Update/ Delete certificates if necessary.

4. ### ****Improvement: Total Count Updates Correctly When Editing Point Counts****

****Issue:**** In the ****Point Count app****, when users edited or deleted point counts for a subject, the Total Count did not update reliably all the time.

- The ****Total Count**** in labeling now updates seamlessly when adding or removing points.
- Ensures a ****smooth and consistent experience**** during labeling and review.

## July 15, 2025

****Improvement:****
We’re excited to introduce a new feature in SAM that enhances instance segmentation workflows. Users can now ****easily find the mask corresponding to a specific instance****, streamlining the identification and interaction process.

****What’s New:****

- Quickly locate the exact mask associated with any given instance.
- Improved usability and efficiency in segmentation tasks.
- Designed to help customers save time and reduce errors.

  ![](../../../assets/media/images/image%28235%29.png)

This update aims to make working with segmented data more intuitive and effective.

## June 23, 2025

Enhanced the ****Segment Anything Model (SAM)**** feedback experience in Visual GPT when working with ****wide or ultra-large media files**** (e.g., 24064px × 2048px).

****Improvement:****

- ****Better Feedback Usability****: Interaction with wide media is now smoother, with more accurate and responsive feedback mechanisms.
- ****Improved Zoom Handling****: Resolved issues where zooming made feedback points appear fuzzy or imprecise.
- ****Scalability Fixes****: SAM now performs more reliably on high-resolution content by addressing segmentation accuracy on scaled-down views.

![](../../../assets/media/images/450457880-7c4395f9-2691-476d-9e79-2cc501f0fd6b.png)

## June 10, 2025

****Improvement:****
A feature to export the application’s summary as CSV or XLSX has been added.

![](../../../assets/media/images/image%28232%29.png)

## May 27, 2025

****Improvement:****
Users are now able to use the "****Deploy Now****" button even when a workflow deployment is scheduled.

This enhancement offers more control and convenience for managing timely updates, while keeping their automated workflow schedule intact.

![](../../../assets/media/images/image%28228%29.png)

You can read more by following [this link](/docs/cogniac-workflow-creation-and-deployment#81-deploy-now).

## May 8, 2025

The HTTP Input application can now scale horizontally through a user-configurable replica count setting. Previously, the replica count was determined automatically based on GPU allocation logic, which was hidden from users. This enhancement introduces an explicit configuration option, improving transparency, scalability, and control.

![](../../../assets/media/images/image%28222%29.png)

You can review the full document [here](/docs/http-input-application-replicas).

## May 8, 2025

****Replay Media Through the root Downstream App****

A new capability has been added to allow users to ****replay media through the entire pipeline starting from a downstream app****—specifically by selecting a ****root upstream application**** from the replay options. This addresses common feedback scenarios where users need granular replay control to curate high-quality datasets from multi-branch pipelines.
![](../../../assets/media/images/image%28219%29.png)

Please check the full document [here](/docs/replay-feature-from-the-antire-pipeline).

## May 8, 2025

****New Role-Based Code Access Restriction in Integration Apps****

As of the latest release, users with roles below `tenant_user` (such as `tenant_viewer`, `tenant_billing`, `tenant_operator` or `annotator`) will no longer be able to view or edit the Code in Integration Apps. These users will not see the ****Code**** tab and will receive a message indicating insufficient permissions (pending frontend message implementation).

For full functionality, users must have one of the following roles: `tenant_user`, `tenant_admin`, `meraki_admin` or higher.

![](../../../assets/media/images/image%28218%29.png)


Please check the full document [here](/docs/integration-app-1).

## April 30, 2025

> Important!
>
> These features are enabled on few tenants only

Implemented improvements for the Point Count App to ensure comprehensive coverage of existing functionality within the Point Count application.

You can check the full document [here.](/docs/point-count-app)

## April 16, 2025

****Improvements for SAM:****

- Keyboard shortcuts were updated for the SAM
- Introduced a Denoise brush size option, allowing users to remove pixel groups using a customizable size that suits their specific needs.

![](../../../assets/media/images/image%28203%29.png)

- Added Polygon Fill option, that helps customers to create a custom-shaped mask.

![](../../../assets/media/images/image%28205%29.png)

- Introduced Polygon Erase tool that allows customers to remove custom shaped pixel clusters.

![](../../../assets/media/images/image%28207%29.png)

- Added the button Save & New, allowing the users directly to complete adding an instance and add a new instance.

![](../../../assets/media/images/image%28209%29.png)

You can see more by following [this link](/docs/segmentation-application#using-the-polygon-tool).

## March 16, 2025

Added multi-polygon tool to annotate areas within an image that straight edge boundaries can be bound (for Segmentation application only, which is a limited beta release).

- Polygon annotation is useful for image segmentation. It precisely identifies and delineates specific regions within an image that can be processed by downstream apps.

![](../../../assets/media/images/image%28197%29.png)

You can see more on the usage by following [this link](/docs/segmentation-application#using-the-polygon-tool).

## February 25, 2025

In the current version, we added a few improvements for you.

## February 6, 2025

****Summary:****

We have introduced a new tabular view to enhance visibility into application performance and feedback. This view provides key details in an easily accessible format, similar to the Tenant Usage table.

Users can navigate the tabular view by going to Usage → Application Summary.

![](../../../assets/media/images/image%28184%29.png)

You will see them listed similarly to the image below.

![](../../../assets/media/images/image%28186%29.png)

****Impact:****

This update enables users to efficiently track application metrics and Model performance at a glance, improving decision-making and operational oversight.

## January 13, 2025

- ****Tenant Expiration notice:****
  Tenant users can now check whether their contract will expire soon and renew it to continue using the tenant as usual. A message informs the tenant Users that the contract is nearing its expiration date.
  Please follow [this link](/docs/tenant-expiration) to view the full document about this change.![](../../../assets/media/images/tenant-expiry-image-gzau6nt6.png)

## January 6, 2025

****Fixed Issue:****

- ****Disassociate Media****: A fix has been implemented to address the issue of media not being disassociated correctly in certain conditions. This improvement ensures better functionality and reliability in media management.
