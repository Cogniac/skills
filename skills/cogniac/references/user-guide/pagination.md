# Pagination

## Overview

Cursor-based pagination is the most efficient method of retrieving bulk resources in the Cogniac API. A cursor refers to an alphanumeric string of characters that mark a specific item in a list of data. Because all results might not be possible to return in a single API call, the results are segmented into pages that you can access via sequential calls using the cursor as the segmentation divider.

```
{
  "data": [
    ...API endpoint data
  ],
  "paging": {
    "next": "https://api.cogniac.io/1/detections/12345?limit=25&after=abcI4250sksldkLKJSDOI"
  }
}
```

The final page will not include the "next" field.

Cursors should not be stored for long periods

If the cursor item in the results/table is deleted, the cursor will be invalidated - therefore, it's best to avoid storing cursors for longer than a session.
