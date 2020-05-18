# AIKIDO 

Toward Straggler Mitigation for Distributed Machine Learning Training in Cloud Data Centers


## Abstract

As artificial intelligence becomes a critical component of everyday life, the popularity of using cloud data centers for training deep neural networks is relentlessly growing. This poses a significant challenge for data center operators where the network bandwidth is shared among multiple ML jobs as well as between ML jobs and data center flows. At high loads, the network experiences transient congestion events frequently which in turn delays the parameter updates between ML workers. Consequently, the training convergence suffers as some workers behind congested links straggle to update the model parameters in time, hence delaying all workers.

We propose AIKIDO as a first step towards mitigating the impact of transient network-induced stragglers on training workloads caused by the dynamic nature of the data center traffic. AIKIDO exploits the inherent robustness of ML training on occasional loss of gradient updates and implements a Skip-Straggler communication strategy where the updates from straggling workers are simply skipped. In addition, AIKIDO introduces an Active-Backup strategy as an improvement to the Skip method to maintain a high accuracy convergence while using fewer resources than full worker replication. In our experiment, we use Google Cloud Engine environment to train ResNet-50 on ImageNet at various scales and demonstrate that AIKIDO is able to mitigate the effect of stragglers and achieve the time-to-accuracy as if there are no stragglers. 

