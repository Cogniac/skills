# Replay from the root application

## Background

This feature request targets replaying media from downstream apps to a specific ****root application**** upstream in the pipeline, not just the immediate upstream app.

---

## Core Feature

****Objective:****
Media from Output Subject will be allowed to replay from the root upstream app

### Implementation Details:

- A new dropdown option, “****Replay Media on Upstream App****,” is added to the Subject Media.

  ![](../../../assets/media/images/image%28226%29.png)
- This dropdown shows only ****root applications**** in the pipeline.

  ![](../../../assets/media/images/image%28227%29.png)
- The root app must be model-based.
- If there are ****multiple root apps****, the user can choose which one to replay through.

  ![](../../../assets/media/images/image%28226%29.png)
- A visual change: the replay modal now includes the full app-subject path, e.g., `test → points`.

> Notes:
>
> - If the app has ****no true upstream root****, the replay option will appear ****grayed out****.
> - There was a workaround script, which is not necessary due to this implementation.
