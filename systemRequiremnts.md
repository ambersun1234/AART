# AART System Requirements
The following are the third-party package that AART require to run

### System package
1. `Ubuntu 16.04 LTS`
2. `OpenPose` fe767ala
3. `Caffe Model`
4. `OpenCV` 3.4.3
5. `gstreamer1.0-libav`
6. `darnet`

### Python package
1. `wxPython` 4.0.4
2. `NumPy` 1.16.2
3. `tensorflow-gpu` 1.12.0
4. `pandas` 0.24.2

### OpenCV compile
+ we choose to compile OpenCV by ourselves
+ if you wish to compile OpenCV, checkout [ambersun1234/linux_setup](https://github.com/ambersun1234/linux_setup/blob/master/__opencv.sh) and follow the instructions to complete task
+ note: due to stability reason, we recommend to use version > `3.4.3`

### OpenPose compile
+ we suggest you to compile OpenPose from source
+ by following [OpenPose official installation guide](https://github.com/CMU-Perceptual-Computing-Lab/openpose#installation-reinstallation-and-uninstallation) or [ambersun1234/linux-setup](https://github.com/ambersun1234/linux_setup/blob/master/__openpose.sh) to install it on your system
+ we recommend you to compile cuda version, due to performance considerations

### darknet compile
+ we use [pjreddie/darknet: Convolutional Neural Networks](https://github.com/pjreddie/darknet) as AART darknet version
+ this version of darknet does not provide windows version, so you need to compile it from source on linux platform
+ by following [Installing Darknet](https://pjreddie.com/darknet/install/) you can install it on your system
+ we recommend you to compile cuda version, due to performance considerations