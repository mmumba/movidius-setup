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

save all changes to an image (not for deployment)


X-server from Docker
http://wiki.ros.org/docker/Tutorials/GUI

Launch ncsdk2 image with (ncsdk2 here is image committed from above container, replace with your image name )
```bash
   docker run --net=host --privileged  \
              --env="DISPLAY"  \
              --env="QT_X11_NO_MITSHM=1" \
              --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
              -v /dev:/dev \
              --name ncsdk2 -it  <image-id>  /bin/bash
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

```bash    
    make examples
    git clone https://github.com/movidius/ncappzoo
    cd ncappzoo/tensorflow/inception
    make run 
```
image should still pop up with correct inference. 
 


# Arch of NCS. Leon + Shave processors:
  you can choose how many shaves a given run gets assigned or chain Movidius NCS on multiple usb ports to get a much higher frame rate than using single NCS.

** history Search on terminal (Ctr-r, Ctr-s)
```bash
   stty -ixon
```