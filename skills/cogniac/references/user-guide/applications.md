# Applications

Applications process incoming media from 'input\_subjects' and associate the media with outbound 'output\_subjects'.

The attributes associated with an individual application include:

| ****Name**** | ****Example**** | ****Description**** |
| --- | --- | --- |
| ****application\_id**** **string** | "di71rG94" | **(read only)** Unique application\_id automatically assigned to each Application object upon creation |
| ****tenant\_id**** **string** | "2ijgkd9we8dksd" | **(read only)** Unique tenant\_id automatically assigned to each tenant object upon creation |
| ****name**** **string** | "Person detector" | Name should be brief and descriptive |
| ****description**** **string** | "Find people walking  into the front door" | A full description of the purpose of the application. Use this field to capture detailed subject and any exceptional feedback instructions. |
| ****type**** **string** | "classification" | **(read only)** Cogniac appliction type. See below for the valid types |
| ****input\_subjects**** **array** | ["flicker\_cats",  "animals\_pics"] | Array of Input Subject id's (note that input subjects' must be already created and have a valid id before adding to an Application) |
| ****output\_subjects**** **array** | ["cat",  "dog",  "face"] | List of subject tags corresponding to objects, patterns, or features that are of interest in this application |
| ****release\_metrics**** **string** | "best\_F1" | The performance measure used when to assess model performance. |
| ****detection\_  thresholds**** **dictionary** | {"cat": 0.5,  "dog": 0.7,  "face": 0.5} | Map between subjects and associated probability thresholds. Detections below the specified probability threshold will not be forwarded to subsequent applications (if any). Detections below the threshold will not be posted to the detection\_post\_urls (if any). |
| ****custom\_fields**** **dictionary**  (Being deprecated, replaced by app\_type\_config) | { "min\_px": 50,  "max\_px": 450,  "stride\_px": 20 } | Field values for application parameters that are unique to a particular application type. |
| ****detection\_  post\_urls**** **array** | ["http://127.0.0.1:9999/  my\_model\_output.net", "https://detections-now.com/detections"] | A list of URL's where model detections will be surfaced in addition to web and iOS interfaces.    Posts are retried for thirty seconds, but URL's that fail retried posts after thirty seconds are blacklisted for five minutes. |
| ****gateway\_  post\_urls**** **array** | ["http://127.0.0.1:9999/  my\_model\_output.net", "https://detections-now.com/detections"] | A list of URL's where model detections will be surfaced from the gateway.    Posts are retried for thirty seconds, but URL's that fail retried posts after thirty seconds are blacklisted for five minutes.    Specifying a gateway post URL implies that the gateway will implement the application along with any linked applications. |
| ****active**** **bool** | true | Flag to control if the the application is active or not. Inactive applications do not process images submitted to their input subjects or requests feed back. |
| ****replay**** **bool** | false | Switch to turn on replay of the input subjects to the app. This is used to 'skim' from the pool of input subject images for the purpose of creating more consensus data. |
| ****refresh\_feedback**** **bool** | false | Flag to control whether the images waiting for user feedback should be re-evaluated by the new model when a new model is released. |
| ****model\_id**** **string** | "Hpo-d-bf30-019ahMzliYY2KT4iWI-YN\_mtsv1\_4426.tgz" | Current model in use by cloud inference. |
| ****staging\_gateway\_model\_id**** **string** | "Hpo-d-bf30-019ahMzliYY2KT4iWI-YN\_mtsv1\_4426.tgz" | Force gateway to use a specific staging model.    If a staging model is specified and the gateway is configured to use staging models, the gateway will download and use the specified model. Likewise for production models.    However, if the gateway is configured to use a production model, but a production model is not specified for a particular application, the gateway will default to using the latest production model. The same logic applies to staging models. |
| ****production\_gateway\_model\_id**** **string** | "Hpo-d-bf30-019ahMzliYY2KT4iWI-YN\_mtsv1\_4426.tgz" | Force gateway to use a specific production model.    If a staging model is specified and the gateway is configured to use staging models, the gateway will download and use the specified model. Likewise for production models.    However, if the gateway is configured to use a production model, but a production model is not specified for a particular application, the gateway will default to using the latest production model. The same logic applies to staging models. |
| ****app\_managers**** **array** | ["user1@email.com", "user2@email.com"] | List of user email address, the users are given the app\_manager role that is authorized to manage application settings and maintain feedback control. |
| ****system **feedback**  per\_hour**** **integer** | 48 | **(read only)** The current target number of feedback requests per hour for the application.    By default this is determined automatically by the system based on the current model performance and the number of subject-media associations that have reached consensus.   The user can over-ride the system selected value by setting the ****requested\_feedback\_per\_hour**** configuration item to the desired feedback level. |
| ****requested **feedback**  per\_hour**** **integer** | 50 | Override the target rate of feedback to surface per hour.    A Null value indicates the system feedback rate should be used.    The default value is Null: system selects feedback rate.    Select a higher value to schedule more feedback feedback requests, or a lower value to schedule fewer feedback requests. |
| ****hpo\_credit**** **integer** | 10 | **(read only)** Based on amount of feedback given, 1 credit is good for **1 immediately prioritized** hyperparameter optimization training run for this application.    Training is scheduled giving priority to higher credit holders. |
| ****created\_at**** **float** | 1455044755 | **(read only)** Unix Timestamp |
| ****modified\_at**** **float** | 1455044770 | **(read only)** Unix Timestamp |
| ****created\_by**** **string** | "test@cogniac.co" | **(read only)** email address of the user who created this application |
| ****current\_  performance**** **float** | 0.9 | \_(read only)\_performance of current winning model based on current validation images with respected to release metrics |
| ****best**model**  ccp\_filename**** **string** | "Hpo-d-bf30-019ahMzliYY2KT4iWI-YN\_mtsv1\_4426.tgz" | \_(read only)\_filename of the current winning model |
| ****last\_candidate\_at**** **float** | 1455044770 | \_(read only)\_timestamp when last model was trained for this app |
| ****last\_released\_at**** **float** | 1455044770 | \_(read only)\_timestamp when last winning model was released for this app |
| ****candidate\_  model\_count**** **int** | 20 | \_(read only)\_number of models trained for this app |
| ****release\_  model\_count**** **int** | 5 | \_(read only)\_number of models released for this app |
| ****training\_data\_count**** **int** | 750 | \_(read only)\_number of training images used by the current winning model |
| ****validation\_data\_count**** **int** | 250 | \_(read only)\_number of validation images used to evaluate the current winning model performance |
| ****inference\_execution\_policies**** **dict** | {  "replicas": 1,  "max\_batch": 8  "runtime\_policy":  {  "rtc\_timeout\_seconds": 5,  "model\_seconds": 0,  "model\_load\_policy": "realtime",  "gpu\_simul\_load": 1,  "gpu\_selection\_policy":  "instance-ix"  }  } | Cogniac EdgeFlows and CloudFlow instances provide a high degree of flexibility for executing application models. Workloads can range from a single application to 100's of simultaneous applications. Different EdgeFlow and CloudFlow models can contain one GPU to dozens of GPUs in clustered environments.    Inference\_execution\_policies controls the tradeoffs between number of applications, application throughput, and GPU memory consumption. Details see below. |

## Inference Execution Policies

Cogniac EdgeFlows and CloudFlow instances provide a high degree of flexibility for executing application models. Workloads can range from a single application to 100's of simultaneous applications. Different EdgeFlow and CloudFlow models can contain one GPU to dozens of GPUs in clustered environments.

The following controls are available on a per-application basis to tune the tradeoffs between a number of applications, application throughput, and GPU memory consumption.

- ****replicas**** The number of instances of the application model that are simultaneously running. Running multiple instances of a model can increase the application throughput when multiple GPUs are available at the expense of more overall GPU memory consumption by the application's models. The default replicas is 1.
- ****max\_batch**** The number of media items that may be batched in a single model inference pass. Increasing the max\_batch size may increase application throughput for smaller media items at the expense of higher latency. The default max\_batch is 1.
- ****runtime\_policy**** specifies controls for managing the scenarios where all applications (including all application replicas) can not fit in GPU memory simultaneously, in which case models must be dynamically loaded and unloaded from GPU memory. Loading and unloading models from GPU memory is relatively slow (temporarily reducing throughput and increasing latency). Furthermore, in highly oversubscribed scenarios there can be large delays in acquiring a GPU with sufficient available memory. These policies allow the tradeoffs to be tuned for different usage patterns.

  - ****runtime\_policy**** consists of the following:

    - ****model\_load\_policy****
    - ****model\_seconds****
    - ****rtc\_timeout\_seconds****
    - ****gpu\_selection\_policy****
    - ****gpu\_simul\_load****

where

- ****model\_load\_policy**** is one of "realtime", "timebound", or "run-to-completion". This controls the policy for UNLOADING a model from GPU memory. This policy is needed because there is a latency associated with loading a model into GPU memory, and potentially an even more significant latency related to finding a GPU with sufficient available memory if the EdgeFlow is highly oversubscribed concerning the number of applications relative to the amount of GPU memory. The default ****model\_load\_policy**** is "realtime".
- The model will never be unloaded with the "realtime" policy (once successfully loaded). This provides the highest sustained throughput for applications processing constant media streams or can not otherwise absorb the latency or potential uncertainty associated with acquiring a GPU with sufficient memory available combined with the subsequent latency of loading the model into memory.
- With the "timebound" policy, a model will be unloaded ****model\_seconds**** (int) after successfully loading. The inference will be complete if the ****model\_seconds**** expires while inference is in progress. Thus, a "timebound" policy with ****model\_seconds**** of 0 always results in the model removal immediately after processing a single media batch. The default ****model\_seconds**** is 0.
- With the "run-to-completion" policy, a model will unload ****rtc\_timeout\_seconds**** (float) after its input queue is emptied of input media items. This policy is helpful for specific periodic application input patterns where the inputs may be somewhat spread out in time. For example, a usage pattern that expects to receive 4 images every 20 seconds, but the 4 images arrive over several seconds would be a good candidate for the "run-to-completion" policy. The default ****rtc\_timeout\_seconds**** is 5.

****gpu\_selection\_policy**** is one of "instance-ix" or "by-free-memory". The default ****gpu\_selection\_policy**** is "by-free-memory".

When the "instance-ix" policy is selected, a model will be assigned to a GPU based on the replica index (0 to replicas - 1) modulo the total GPU count. This is more deterministic and most appropriate for realtime applications.

When "by-free-memory" policy is selected ****gpu\_simul\_load**** controls the number of models that are allowed to contend for a give GPU's available memory simultaneously. This is only relevant if there are many 10s of apps contending for each GPU. The default gpu\_simul\_load is 1.
