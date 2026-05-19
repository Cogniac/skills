# Release Notes — 2021

## December, 2021

Enhancements

- Improved contrast enhancement speed and acuity
- Added search for workflows in deployment group view

![](../../../assets/media/images/image-1700613394700.png)

- Added point count data in thumbnail view

New feature

- Added Time-based One-Time Password(TOTP) Multi-factor Authentication support ![](../../../assets/media/images/image-1700613444656.png)

## November, 2021

New feature

- Added a search for workloads in the deployment status
- Edit applications during workflow creation

Enhancements

- Bug fixes for workflow creation.
- Force links in the drop-down to occupy the complete row.

## October, 2021

Enhancements

- Deprecated Area Detection V1 application type
- Support force feedback to CloudCore in EdgeFlow upload policies for probability range policy ![](../../../assets/media/images/image-1700528020999.png)

## September, 2021

Enhancements

- Support for Workflow Deletion

![](../../../assets/media/images/image-1700592208474.png)

- Added sort by media timestamp to subject

![](../../../assets/media/images/image-1700592163455.png)

## August, 2021

New feature

- Added a visual tool for creating new workflows
- Replay for OCR applications supports filter by specific OCR string
- Added filter by subject to media search results

  ![](../../../assets/media/images/image-1700592269654.png)


- Added selector for build version in integration app

![](../../../assets/media/images/image-1700592345724.png)

Enhancements

- Allow re-targeting of the EdgeFlow model at the time of workflow cloning.

![](../../../assets/media/images/image-1700593121360.png)

- Workflow views highlight the difference between workflow app configurations and current CloudCore application configurations.                                           ![](../../../assets/media/images/image-1700593080615.png)
- Added option to stop existing replay           ![](../../../assets/media/images/image-1700592576127.png)
- Fix for graph compression hotkey.

## July, 2021

New feature

- Added support for a new consensus type called "Sidelined" which allows users to specify a media not to be used for model training/validation purposes. ![](../../../assets/media/images/image-1700613255682.png)
- Add a workflow pipeline view.  ![](../../../assets/media/images/image-1700606305283.png)

Enhancements

- Highlight applications with pending feedback in the app drop-down in the graph. ![](../../../assets/media/images/image-1700613214845.png)
- changes to persist user feedback in queue.
- Fix for shading inactive applications in graph visuals.

## June, 2021

New feature

- Added app type config for point count detection

![](../../../assets/media/images/image-1700608098927.png)

Enhancements

- Group applications that share common upstream and downstream applications if there are 20 or more of them to make the pipeline more readable.

![](../../../assets/media/images/image-1700608147942.png)

- Add subject search for model evaluation toolbar when there are greater than 50 subjects

## May, 2021

New feature

- Added Contrast filter

![](../../../assets/media/images/image-1700608211954.png)

- Added the ability to clone workflows

![](../../../assets/media/images/image-1700608242914.png)

- Added option to edit reference focus for subject reference media ![](../../../assets/media/images/image-1700608519405.png)

## April, 2021

New feature

- Added IPC Inputs application
- Added pre-load software on workflow ![](../../../assets/media/images/image-1700609385896.png)
- Added workflow view

## March, 2021

New feature -

- Added reference media id to subjects

![](../../../assets/media/images/image-1700609614852.png)

- Added deployment groups and workflows

  ![](../../../assets/media/images/image-1700609666970.png)

Enhancements

- Added auto-complete to integration code editor
- Added Flake8 linting for integration code

## February, 2021

New feature

- Added EdgeFlow deployment view
- Added integration app streaming logs ![](../../../assets/media/images/image-1700609920704.png)
- Added API key creation and management to users  ![](../../../assets/media/images/image-1700609982512.png)
- Added ability to share media via email with other tenant users ![](../../../assets/media/images/image-1700610067864.png)

Enhancements

- Support model "donation" between apps of the same type within a tenant ![](../../../assets/media/images/image-1700610172130.png)

## January, 2021

Enhancements

- Enhance replay function to support time ranges ![](../../../assets/media/images/image-1700611439578.png)
- Feature to lock EdgeFlow to disable config or model updates ![](../../../assets/media/images/image-1700611880300.png)
- Added subjects info to media search results ![](../../../assets/media/images/image-1700612027262.png)
- Added Emacs and Vim keybindings to the code editor
