# movidius-setup
"deploying on movidius"



Using Docker setup method on:
https://movidius.github.io/ncsdk/docker.html

```bash
   $ docker build -t ncsdk -f ./extras/docker/Dockerfile https://github.com/movidius/ncsdk.git#ncsdk2
```
Create container.

```bash
   docker run --net=host --privileged -v /dev:/dev --name ncsdk -i -t ncsdk /bin/bash
```


copying file into docker
```bash
   docker cp live-camera-v2.py <Container-ID>:/ncsdk/examples/tensorflow/inception_v3/
```
Copy from container to host
```bash
   docker cp <Container-ID>:/ncsdk/examples/tensorflow/inception_v3/live-camera-v2.py live-camera-v2.py    
```

Save all changes to an image (not for deployment, image saved this way is large... to create a reasonably sized docker, include all steps in a Dockerfile and build)

Exit docker container and commit image with:
```bash 
  docker commit <CONTAINER-ID> ncsdk-version1
```
Check that image is saved

```bash
   docker image ls | grep "ncsdk"
```
Remove any unwanted images

```bash
   docker image rm <IMAGE-ID>
```


X-server from Docker
http://wiki.ros.org/docker/Tutorials/GUI

Launch ncsdk2 image with (ncsdk2 here is image committed from above container, replace with your image name )
```bash
   docker run --net=host --privileged  \
              --env="DISPLAY"  \
              --env="QT_X11_NO_MITSHM=1" \
              --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
              -v /dev:/dev \
              --name ncsdk2 -it  <IMAGE-ID>  /bin/bash
```

Other ways to connect to container with display.
```
https://github.com/fcwu/docker-ubuntu-vnc-desktop

```

NCAPI
```
https://movidius.github.io/ncsdk/ncapi/ncapi2/py_api/readme.html
```

Compiling graph, make sure you refer to correct image to get the right CNN layer names for flag "-on"

```bash
   $ mvNCCompile output/inception-v3.meta -in input -on  InceptionV3/Predictions/Softmax -o graph -is 299 299 -s 12
``` 



# NOTES

Installing and avoiding SDK and API version conflicts.

# NCSDK V1 and NCSDK v2
some confision of mixing downloads from ncsdk2 and ncsdk1 (ncs)

check versions after docker install with 
```bash
  cat /opt/movidius/version.txt
```

'make run' errors popping up of nonexistent functions arise from mismatch of SDK version.
Running docker the following worked with test image inference run popping up after enabling xserver/display forwarding on docker.

```bash
    mkdir -p ~/workspace
    cd ~/workspace/
    git clone https://github.com/movidius/ncsdk.git
    cd ncsdk/
    make install
```
'make install' throws an error: "Installation failed. Error on line 630"
but make examples still works afterwards.
If you specifically want NCSDK2, use

```bash
   git clone -b ncsdk2 https://github.com/movidius/ncappzoo.git
```
from: https://github.com/movidius/ncappzoo/
Note: "At some point in the future the NCSDK 2.x projects will move to the master as 1.x becomes obsolete."

```bash    
    make examples
    git clone https://github.com/movidius/ncappzoo
    cd ncappzoo/tensorflow/inception
    make run 
```
image should still pop up with correct inference. 


If you need to kill container:

```bash
   docker contianer kill <CONTAINER-ID>
```

Clean up all exited containers 

```bash
   sudo docker ps -a | grep Exit | cut -d ' ' -f 1 | xargs sudo docker rm
```

# Arch of NCS. Leon + Shave processors:
  you can choose how many shaves a given run gets assigned or chain Movidius NCS on multiple usb ports to get a much higher frame rate than using single NCS.

** history Search on terminal (Ctr-r, Ctr-s)
```bash
   stty -ixon
```




** Check Tensorflow version
```bash
   python3 -c 'import tensorflow as tf; print(tf.__version__)'  # for Python 3
```
(got 1.4.0 with default docker container and no "..tensorflow/tools/graph_transforms" location.





** Installing Bazel
```
https://docs.bazel.build/versions/master/install-ubuntu.html
```
