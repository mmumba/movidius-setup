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

