# Point-Count App

The ****Cogniac Point Count Application**** enables automated, AI-driven object counting within images and videos. It is ideal for use cases where you need to count distinct instances of a particular subject (e.g., people, cars, parts) with precision and scalability.

---

## What Is the Point Count App?

The ****Point Count App**** is a specialized application within the Cogniac platform that:

- ****Detects and counts**** visible instances of a specific object in visual media.
- ****Generates accurate count labels**** that can be used for reporting, quality assurance, or triggering downstream workflows.
- ****Learns from human feedback**** to continuously improve performance.

---

## Application Configuration

### Step 1: Create a New Count Application

1. Log into your ****Cogniac account****.
2. Go to ****Application Builder****.
3. Select ****“Point Count”**** as the application type.
4. Name your application (e.g., `Inventory Shelf Counter`, `Worker Count Line 2`).

### Step 2: Set Subjects

- ****Input Subject****: Defines the incoming media to analyze.
- ****Output Subject****: Stores the processed results (typically the same as the input subject).

### Step 3: Set Parameters

- `min_count`: Smallest number of objects expected in the image (default is `0`).
- `max_count`: Largest number of expected objects (helps optimize detection and training performance).

---

## Uploading and Processing Media

1. Upload images or videos to the ****input subject****.
2. The application analyzes each media item and returns:

   - An object count
   - Visual overlays of counted instances
   - Confidence scores (optional)

---

## Providing Feedback (Essential for Training)

Cogniac’s Point Count model is refined through ****user feedback****.

### How to Provide Feedback:

- Open a processed image in the UI.
- Confirm or correct the point ****count value**** shown.
- The corrected count is stored in the `app_data` field with:

  - `app_data_type`: `"count"`
  - `value`: An integer representing the correct count

As you submit feedback:

- The model ****re-trains periodically****.
- It ****automatically adjusts**** the `min_count` and `max_count` values if needed.

---

## Output & Insights

The Point Count App outputs:

- Count values for each image
- Summary analytics via dashboards (optional)
- Count-based event triggers via API (e.g., send alert if `count > 10`)

All outputs are stored in the ****output subject**** and accessible through the Cogniac API or UI.

---

## Data Privacy & Model Control

- All data is processed securely within the Cogniac platform.
- You maintain full control over your application, subjects, and training data.
- Access is role-based for added security.

---

## Best Practices

- Use high-resolution images for better accuracy.
- Regularly review and correct results, especially early in deployment.
- Choose `min_count` and `max_count` wisely to set expectations.
- Keep subject naming consistent and descriptive.
