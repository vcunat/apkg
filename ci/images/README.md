# apkg CI images

## build image

use `build.sh` to build docker image, for example:

```
./build.sh python-current
```

## upload image into apkg CI

you need to login first:

```
$ docker login registry.nic.cz
```

then you can use `upload.sh` script:

```
./upload.sh python-current
```
