Docker Build
------------

* python-current (for python-$VER replace "current" with "$VER")

```
$ docker build --no-cache -t registry.nic.cz/packaging/apkg/ci/python-current:apkg python-current

$ docker login registry.nic.cz
$ docker push registry.nic.cz/packaging/apkg/ci/python-current:apkg
```
