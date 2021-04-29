# apkg CI images

## build image

use `build.sh` to build docker image, for example:

```
./build.sh debian-10
```

## upload image into apkg CI

you need to login first:

```
$ docker login registry.nic.cz
```

then you can use `upload.sh` script:

```
./upload.sh debian-10
```
