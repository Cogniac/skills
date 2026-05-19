# Leaderboard Feature Summary

## ****Overview****

Leaderboard Feature Summary - The Leaderboard feature allows you to compare the performance of the top N models released for an already trained application.

- This table shows statistics for the top N models based on ‘GPU FPS’, ‘GPU memory’, ‘GPU throughput’, and ‘Primary App Result’ metrics.
- You can sort columns in ascending or descending order by selecting the arrow in the table header.

![](../../../assets/media/images/image%28168%29.png)

The Leaderboard feature includes Models of different Inference Precision, such as INT8, FP16, and FP32. Detailed information about these precision Models can be found below.

- FP32 (32-bit floating point) has long been the standard format for neural network computations and has been the primary choice in deep learning for many years. By default, weights, activations, and other neural network values were typically represented in FP32.
- FP16 - (16-bit floating point) is increasingly favored over FP32 (32-bit floating point) in deep learning because lower precision calculations are often sufficient for neural networks. The added precision of FP32 offers minimal benefit while being slower, consuming more memory, and reducing communication speed. FP16 is commonly used for mixed-precision training in frameworks like TensorFlow and PyTorch and for post-training quantization to enable faster Inference, such as in TensorFlow Lite.
- INT8 - an 8-bit Integer (INT8) uses a fixed number of bits to represent whole numbers and is commonly employed in quantization techniques to reduce the model size and enhance inference speed. We currently offer INT8 models that are supported on T4 GPUs.

The precisions supported by each of the {{glossary.Applications}} are below.

- Character Recognition (OCR): FP32
- Box Detection: FP16, INT8
- Area Detection: FP16
- Classification: FP16
- Static Count: FP16
- Detection: FP16
- Point Detection: FP16

Currently, we offer two types of leaderboards based on hardware support:

1. ****Mixed Precision Leaderboard**** – This includes all the models, both INT8 and non-INT8 (FP16, FP32).
2. ****INT8 Precision Leaderboard**** – This is exclusively for box detection apps.

![](../../../assets/media/images/image%28166%29.png)

In some cases, there may be a mismatch between the consensus\_release\_id. Below are the potential reasons for this mismatch:

- A mismatch in consensus\_release\_id means that the mixed precision and INT8 leaderboards were evaluated on different dataset versions. A fair comparison between the two leaderboards must be evaluated using the same dataset version. If there is a mismatch, it indicates that the datasets have been updated or changed between evaluations, which can affect the results. The consensus\_release\_id is highlighted in red if they have a mismatch.
- Each time the dataset is updated—whether through the addition of new labeled images, label updates, or the deletion of labeled images—a new consensus\_release\_id is generated. Since model evaluations occur asynchronously in a distributed environment, we cannot guarantee that all models will be evaluated simultaneously. Eventually, both leaderboards will align with the same consensus\_release\_id, but there may be a period where one is updated before the other. The timing of these updates depends entirely on how frequently the dataset changes.

The ‘Show Subjects’ button toggles the display of output subject statistics when there is more than one Output Subject.

 ![](../../../assets/media/images/image%28167%29.png)

Values displayed are based on the T4 GPU.

## ****Leaderboard Updates when:****

1. Evaluation metric changes - release metric, any threshold.
2. Whenever a different model (newly trained or older trained) enters the leaderboard of the top N models.
3. A new consensus has been released.

Below the Leaderboard tab, the following information is displayed:

Consensus\_release\_ID and time of the latest release (Consensus\_release\_time).

The time when the Leaderboard last synced (Leaderboard\_time).

![](../../../assets/media/images/image%28165%29.png)

## ****Benefits of the Leaderboard feature****

1. Quickly compare top models on key performance metrics.
2. Monitor improvements from ongoing model training.
3. Identify best versions for production deployment.
4. See the model performance on each output subject individually.
