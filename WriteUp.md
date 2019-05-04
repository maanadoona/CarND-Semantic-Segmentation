# Semantic Segmentation
### Introduction
In this project, you'll label the pixels of a road in images using a Fully Convolutional Network (FCN).

### Implementation
##### Fully Convolutional Networks
![FCN](./result/FCN.png)

##### Parameters
Parameter |Test A                   |  Test B
:--------:|:-------------------------:|:-------------------------:
Kernel Init stddev | 0.01             |  0.01
l2_regularizer     | 0.0001           |  0.001
Learning Rate      | 0.0001           |  0.0009
Batch Size         | 2                |  5


### Result
#### Outputs
Here are results of Test A vs. Test B

Result A                   |  Result B
:-------------------------:|:-------------------------:
![A1](./result/um_000003.png)  |  ![B1](./result/ref/um_000003.png)
![A2](./result/um_000006.png)  |  ![B2](./result/ref/um_000006.png)
![A3](./result/um_000061.png)  |  ![B3](./result/ref/um_000061.png)


#### Loss and IoU
![LossAndIoU](./result/LossAndIoU.png)



