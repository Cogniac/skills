# Subject Media Associations

## Subject-media associations

The Subject-Media Associations are the main way that different types of information are linked to visual media in the Cogniac system. All predictions made by the model and user feedback generate subject-media associations that vary in probability according to the strength of the association. It’s important to note that a subject-media association probability of 1 indicates a strong positive association (meaning the subject is present). In contrast, a probability of 0 indicates a strong negative association (meaning the subject is not present).

The Cogniac system constantly assesses the accuracy of both user feedback and application model predictions (based on user feedback). User feedback is cross-validated against other user feedback to assess individual user feedback accuracy. Application model predictions are validated against user feedback to determine model accuracy. These assessments occur within a Bayesian statistical framework that treats users and models almost identically. The only difference is that there is a baseline assumption that, on average, our users are better than random, e.g., not evil. We prefer not to have to relax that assumption...

Based on these assessments, after any model prediction and after any user feedback, the system takes into account all available information to update the subject-media association probability appropriately for the media item and associated subject.

Subject-media associations that have received user feedback and have sufficiently low uncertainty (below 5% by default) are declared as 'consensus' subject-media items. These consensus items are considered to be reliable enough to be used for model training. Consensus items are denoted by a green check mark for positive association and a red x for a negative association within the Cogniac web applications.

Advanced Cogniac application types (such as counting and measurement applications) can include additional information within a subject media association. For example, an image could be associated with a subject "horse" and a count of 3, indicating to the system that there are three horses in the image. In all cases, the information is anchored by and serves to qualify the subject as it pertains to a particular media item.
