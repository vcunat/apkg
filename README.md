# apkg

apkg is **going to be** Free and Open Source minimalist cross-distro packaging
automation tool aimed at producing **high quality packages** for many different OS
distributions/packaging systems with minimum overhead.


## why?

There are *many* different packaging tools, but none of them provided me with
satisfactory packaging automation that allows creating high quality packages
for different distros such as Debian, Arch or Fedora directly from upstream
repos with ease.

I've already created
[rdopkg](https://github.com/softwarefactory-project/rdopkg) that tackles
automated packaging of hundreds of RPM packages across different projects,
distros, versions, and releases but it's bound to RPM packaging only and thus
it's useless outside of Fedora/CentOS/RHEL.

`apkg` is going to inherit good features and principles of `rdopkg`
(determined and refined after > 5 years in production) without the accumulated
bloat and more importantly without the chains of a specific platform.

I'd much prefer to use an established tool that already exists, but to my
knowledge and experience, there is simply no such tool in existence at this
time. I hope to describe flaws of various existing packaging tools and
systems in the future but... *let me show you some code first, yes?*


## status

**development just started, please see**
[apkg design wiki page](https://gitlab.nic.cz/packaging/apkg/-/wikis/design) -
comments welcome!

**ᕕ( ᐛ )ᕗ**


## installation

`apkg` is going to provide various packages of itself once it's useful, but
for now please use the source.


### requirements

Python module requirements are listed in [requirements.txt](requirements.txt).

They are installed automatically by `setup.py`.


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

* docs
* tests
* packaging
* much more
