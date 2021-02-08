# tinyFPS
use FPGA to accelerate the Farthest Point Sampling operation

# what is FPS

Farthest Point Sampling  is a important operation using in PointCloud Sampling. For a PointCloud P, this operation downsample a small pointset S.

# Why we accelerate the FPS

FPS is a normal operation for PointCloud. In recent study, we find this operation has long running  time. 

e.g.(modelnet40, Nvidia 1080Ti)

| num_point | num_sample | runtime(ms)|
| :-: | :-: |:-:|
|1024 | 32 | 11.3|
| 1024 | 64 | 17.5|
| 1024 | 128|32.4|
| 1024 | 256 | 64.1| 

# How to accelerate

we will design a parallel architecture to excute it more efficiently by data reuse and overlapping the transformation and calculation stage, and using the Xilinx HLS tool to implement this architecture.

