# Optical Character Recognition (OCR) Application

## Optical Character Recognition Application

Optical Character Recognition (OCR) applications identify letters, numbers, and spaces in media. Due to the potentially infinite combinations of characters that can be observed, OCR applications use a single output subject to associate media with the specific identified characters listed in the subject-media association's app\_data.

## Creating an OCR Application

OCR applications require the following fields:

1. An application name, e.g., 'License Plate Reader'.
2. A list, output\_subjects, with a single output subject to identify within the input media, e.g., 'license\_plates'.
3. An optional list, input\_subjects, of one or more subjects to store input media. It can be output subjects from other Cogniac applications.
4. A string, character\_set, of characters to identify. OCR applications are case-sensitive; i.e., 'AaBbCc' will identify both cases of the letters 'A', 'B', and 'C'.
5. An integer, max\_characters, denotes the length of character strings to identify in media. For example, a license plate reader focused on California license plates could use a max character length of 7. Spaces can be used to denote missing characters.

You can see the complete OCR app creation flow → [[Here]](/docs/creating-an-optical-character-recognition-app-ocr).

To view additional, optional application creation fields and their default values, see [Applications - Create](/docs/applications-create).

## OCR Feedback

When providing feedback in an OCR application, only one output subject is required, as the characters identified are specified in the subject-media association's app\_data field with an app\_data\_type of ocr.

Negative OCR Subject-Media

False or empty subject-media associations are not accepted for an OCR application. However, an empty OCR detection can be made by passing an OCR value of " ", a number of spaces equal to max\_characters (space must be included as an allowed character).

For best results, it is recommended to use either a ****Detection**** or ****Box Detection**** application to identify the media or focus areas of media that are positively associated with characters being present.

For example, a license plate reader OCR application can use the output of a license plate region detection application that identifies a box region in an automobile image containing the license plate. As a downstream application, the OCR application will receive the license plate detection application output as subject-media focus areas, and only the boxed region identified by the detection application will be processed for character recognition.
