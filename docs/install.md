# apkg installation

`apkg` is going to provide various packages of itself once it's useful, but for now **please use the source**.


### requirements

Required **python modules** are listed in {{ 'requirements.txt' | file_link }}:

{{ 'requirements.txt' | file_text }}

Once you have `pbr` (`python3-pbr`) installed, rest of required modules can be
automatically installed by `setup.py`.

Furthermore, `apkg` currently relies on following external tools available
from most distro repos:

* `git` to handle `git` repos
* `atool` to handle archives

Python modules needed to build `apkg` docs are listed in {{ 'doc-requirements.txt' | file_link }}:

{{ 'doc-requirements.txt' | file_text }}



### user development install

I use this for python projects I develop actively:

```
git clone https://gitlab.nic.cz/packaging/apkg
cd apkg
python3 setup.py develop --user
```

This creates a link in `~/.local/lib/python3.X/site-packages/apkg.egg-link`
and also installs `apkg` script into `~/.local/bin` so make sure you have
`~/.local/bin` in your `$PATH`, possibly before system `bin` paths to override
`apkg` scripts provided by system packages.


### virtualenv install

If you don't want to taint your system by `develop` method above and/or you
want `apkg` isolated from the rest of your system, you can use `virtualenv`
(`python-virtualenv` package on most distros):

```
git clone https://gitlab.nic.cz/packaging/apkg
cd apkg
virtualenv venv
source venv/bin/activate
python3 setup.py develop
apkg
```

You can enter the `venv` later/from other terminals by

```
source apkg/venv/bin/activate
```

You can also do this little trick inside `venv` to avoid conflicts with system `apkg`
packages (assuming `~/bin` is in your `$PATH`):

```
source apkg/venv/bin/activate
ln `which apkg` ~/bin/apkg-dev
apkg-dev
```
