# apkg installation

`apkg` is going to provide various packages of itself soon,
but for now **please use the source**.


## requirements

You need **Python >= 3.6** and `pip`.

Python 3.5 is EOL and unofficially supported on best-effort basis in `apkg`
until Debian 9 Stretch LTS EOL June 30, 2022.

Install following downstream packages using your package manager:

* `python3-setuptools`
* `python3-pip`

<<<<<<< HEAD
* `git` to handle `git` repos
=======
Debian/Ubuntu example:
>>>>>>> 1145742 (packaging: refactor and drop pbr)

```
apt install python3-setuptools python3-pip
```

Other python requirements should be **handled automatically**, they are
listed and briefly explained in {{ 'requirements.txt' | file_link }}.

Python modules needed to build `apkg` docs are listed in
{{ 'doc-requirements.txt' | file_link }}.


## install from source

Make sure you're in the top `apkg` source dir:

```
git clone https://gitlab.nic.cz/packaging/apkg
cd apkg
```

Then choose one of installation methods below:


### user install

Fastest and recommended way to install from source for CLI usage without affecting the rest of your system is to get
[pipx](https://pipxproject.github.io/pipx/installation/)
and then simply run:

```
pipx install .
```

This installs `apkg` into `virtualenv` without affecting rest of your system
while only exposing `apkg` CLI script.

`pipx install` also features convenient `--editable` mode.

If you're using `apkg` python module or you don't want to use `pipx`, you can
use local user `pip install`:

```
pip install --user .
```

Or the old-fashioned equivalent through `setup.py` but that's using
`easy_install` which is worse than `pip`:

```
python3 setup.py install --user
```


### editable/develop install

For development it's nice when source changes immediately apply and that
can be done with editable/develop install.

Old-fashioned and well tested develop install using `setup.py` has the advantage of making `apkg` module available to other python modules:

```
python3 setup.py develop --user
```

This creates a link in `~/.local/lib/python3.X/site-packages/apkg.egg-link`
and also installs `apkg` script into `~/.local/bin` so make sure you have
`~/.local/bin` in your `$PATH`, possibly before system `bin` paths to override
`apkg` scripts provided by system packages.

When you need CLI only, it's recommended to use `pipx` instead in `--editable` mode:

```
pipx install -e .
```

Upstream python discussions recommend `pip install --editable .` but that has
the fatal flaw of currently not working with local `--user` install. You can
use it inside disposable container or a VM but I'd never taint my system
python installation with a global install like that.


### virtualenv install

If you don't want `apkg` installation to affect your system but don't want
to/can't use `pipx`, you can use `virtualenv` directly (`python3-venv`
package usually):

```
git clone https://gitlab.nic.cz/packaging/apkg
cd apkg
virtualenv3 venv
source venv/bin/activate
python3 setup.py install
apkg
```

You can enter the `venv` later/from other terminals by

```
source apkg/venv/bin/activate
```
