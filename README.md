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

NCAPI
https://movidius.github.io/ncsdk/ncapi/ncapi2/py_api/readme.html