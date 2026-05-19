# Count Application

## Count Applications

Count applications identify the number of instances in which a single subject is positively associated with a media item.

## Creating a Count Application

Count applications require the following fields:

- An application name, e.g., 'Car Counter'.
- A list, output\_subjects, with a single output subject to identify within the input media, e.g., 'car'.
- An integer, min\_count, denotes the minimum allowable number of instances of the subject in media. If, during feedback, a user asserts that less than min\_count instances of a subject are present, the application will automatically update the min\_count value to reflect that.
- An integer, max\_count, denotes the maximum allowable number of instances of the subject in media. If, during feedback, a user asserts that more than max\_count instances of a subject are present, the application will automatically update the max\_count value to reflect that.

To view additional, optional application creation fields and their default values, see [Applications - Create](/docs/applications-create).

You can see the complete Count app creation flow → [[Here]](/docs/creating-a-count-application).

## Count Feedback

When providing feedback in a Count application, only one output subject is required, with the total count of subject instances identified in the subject-media association's app\_data field, with an app\_data\_type of count.
