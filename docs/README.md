# apkg - packaging automation tool

apkg is **going to be** Free and Open Source minimalist cross-distro packaging
automation tool aimed at producing **high quality native packages** for many
different OS distributions/packaging systems with minimum overhead.


## status

**development started recently**

* [apkg design](design.md)
* [source code](https://gitlab.nic.cz/packaging/apkg)
* [merge requests](https://gitlab.nic.cz/packaging/apkg/-/merge_requests)
* [issues](https://gitlab.nic.cz/packaging/apkg/-/issues)

patches, issues, comments and other contributions are welcome **ᕕ( ᐛ )ᕗ**


## installation

`apkg` is going to provide various packages of itself once it's useful, but
for now please use the source.


### requirements

Python module requirements are listed in `requirements.txt`.

Once you have `pbr` (`python3-pbr`) installed, rest of requirements can be
automatically installed by `setup.py`.


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

## usage

Simply run

```
apkg
```

to get summary of available commands (equivalent of `apkg --help`).

Use `--help`/`-h` after a command to get help for that particular command instead:

```
apkg status --help
```

## contact

Use [gitlab issues](https://gitlab.nic.cz/packaging/apkg/-/issues)
to communicate anything you have in mind. Feedback is most appreciated!


## planned features

* tests & CI
* more docs
* packaging
* much more
