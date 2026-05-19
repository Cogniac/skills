# Create and maintain an Access Control List (ACL)

## Overview

This document provides instructions for users to submit requests for Python packages and Base Container Images to be reviewed for approval within the integration application. If approved, these packages will be available for selection in a drop-down list within the integration application.

## Package Submission Notifications

- Upon submitting a package, the user will receive an email confirming the submission.
- After the review process, the user will be notified of the approval status via email, indicating whether the package is valid or invalid.

## Background Vulnerability Scanning

- Vulnerability scanning is essential for safeguarding users' Python packages. Our system performs and ensures that users receive timely scan results via email notifications.

## Selection Availability

- Once a Package or a Base Container Image has been selected, it won’t be available in the drop-down list within the integration application.

## Step-by-step process:

There are two options:

1. Add a package - Click the "+" button next to "Add a package for review.” or select an existing and approved package from the drop-down list.

![](../../../assets/media/images/create-and-maintain-an-access-control-list-acl2-image-nvckd5vp.png)

> Important:
>
> Users need to keep in mind that the Python package must exist in PyPI otherwise an error will be thrown.

![](../../../assets/media/images/create-and-maintain-an-access-control-list-acl2-image-vhdki23f.png)

2. Add a base container image by clicking on the ‘+’ following “Add a Base Container image for review.” or select it from the drop-down list.

![](../../../assets/media/images/create-and-maintain-an-access-control-list-acl2-image-sor2n4qo.png)

3. Save and Build the package
    ![](../../../assets/media/images/create-and-maintain-an-access-control-list-acl2-image-5c8jgtv1.png)

- Once a package has been submitted, the user will receive an email with the status of the package so they can be aware of whether it is accepted or not.

****status: pending**** If the user notices that the status of a package remains in a pending state for too long, they need to contact support at: support@cogniac.ai ![](../../../assets/media/images/create-and-maintain-an-access-control-list-acl2-image-7a6c7274.png)

****status: valid**** If the validation was successful, the user will receive an email with the status, similar to the image below:
![](../../../assets/media/images/create-and-maintain-an-access-control-list-acl2-image-ibokh3y0.png)

****status: failed**** If the package validation has failed, the user will be able to see the build appear in the “Failed Builds” section.

![](../../../assets/media/images/create-and-maintain-an-access-control-list-acl2-image-rwvbd8fq.png)

- Tooltip Check: Hover over the tooltip for any additional details or clarifications if needed.

![](../../../assets/media/images/create-and-maintain-an-access-control-list-acl2-image-c2lh0d2y.png)![](../../../assets/media/images/create-and-maintain-an-access-control-list-acl2-image-myy0fjez.png)
