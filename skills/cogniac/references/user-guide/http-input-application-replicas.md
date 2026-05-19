# HTTP Input Application replicas

### ****Summary****

The HTTP Input application can now scale horizontally through a user-configurable replica count setting. Previously, the replica count was determined automatically based on GPU allocation logic, which was hidden from users. This enhancement introduces an explicit configuration option, improving transparency, scalability, and control.

---

### ****Change Overview****

- ****New Capability****:
   Users can override the internal scaling logic and explicitly set the number of replicas for HTTP Input applications.
- ****Default Behavior****:
   The default value for this setting is `"Auto"`, preserving the existing scaling logic.
  ![](../../../assets/media/images/image%28220%29.png)
- ****UI Location****:
   `HTTP → App Settings → Application Configuration`

  ![](../../../assets/media/images/image%28221%29.png)
- ****New UI Control****:
   A dropdown labeled ****"Number of Replicas"**** with selectable values:

  - ****Auto****
  - ****1 to 8****
- ****Technical Behavior****:

  - Each replica can handle up to 16 concurrent requests and is based on the number of input subjects.
  - As the number of replicas increases, increased CPU memory usage results in contention with other EdgeFlow/CloudFlow subsystems.
  - This configuration helps handle high-throughput workloads by allowing horizontal scaling:

    Example: For a system with 4 GPUs and 8 replicas of a model and a single Input subject into the HTTP input app, the number of HTTP input apps should be set to 4 to handle 32 concurrent transactions
  - Leaving the value set to “Auto” will allow provisioning the HTTP Input app based on the number of input subjects and the model of the EdgeFlow/CloudFlow.
