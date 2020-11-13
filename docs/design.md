# apkg design

## general goals

`apkg` must make it easy to package software for various operating system distributions directly from upstream.

`apkg` should follow conventions and best practices of individual distributions as opposed to forcing a custom approach.

`apkg` must be minimalist and maintainable. It should reuse existing tools and only provide glue and reasonable conventions required to use these tools together across different distributions.

`apkg` must be pleasant to use from interactive terminal sessions, shell scripts, python scripts (as a module), and in CI systems.

`apkg` should be smart and infer as much information from environment as possible in order to require no or little parameters to perform its duties. This must be transparent and still allow fine control. If human can do it, machine can too.

`apkg` should lead by example by using and promoting the best packaging practices and providing reasonable conventions and defaults for projects that wish to do packaging right.

`apkg` should be replaceable. Projects following `apkg` conventions should be able to continue packaging (with few scripts of their own probably) even if they chose to drop `apkg`.


## concepts

* **repo**: `git` (or other VCS) repository containing project sources
* **archive**: archive containing project source code (also known as tarball).
  * **upstream archive**: official upstream archive
  * **dev archive**: development archive created locally from project repo
* **distro**: operating system distribution such as Debian, Fedora, Arch, NixOS, etc.
* **package**: package archive accepted by a package manager of particular OS distribution
* **source package**: files needed in order to build a package (this varies a lot between distros, for example RPMs are built from a single `.src.rpm` source package while `.deb` packages are built from several files)
* **packaging style**: processes associated with packaging for specific family of distros (for example `deb` packaging style is used on Debian, Ubuntu, and their clones)
* **packaging template**: files needed to build a source package; this could be called "packaging sources" but I suggest using "template" instead in order to avoid confusion with "source package".


## input

Project repo is expected to have a top-level `distro` directory containing all **input** files required for packaging. **`distro/` is strictly input-only directory.** Files there shouldn't ever be modified in-place during `apkg` operations unless requested and no additional files (such as build files or logs) must be created there.

```
distro
├── config                 <- apkg configuration and other files such as custom plugins/packaging styles
│   ├── apkg.toml
│   └── plugins
├── common                 <- shared packaging files such as systemd services
│   └── project.service
└── pkg                    <- packaging templates - source packages are built from these files
    ├── arch
    │   └── PKGBUILD
    ├── deb
    │   ├── changelog
    │   ├── control
    │   └── rules
    └── rpm
        └── project.spec
```

This structure has few advantages over individual packaging directories directly in root as seen in the wild (`debian/`, `rpm/`, ..):

* not spamming project root with multiple arbitrary directories (which might collide with existing dirs)
* having all packaging files in one place (easier to notice/update all of them, nicer diffs, ...)
* in case of `debian/`, not colliding with downstream `debian/` dir - projects are recommended not to include such directory in upstream tree

Furthermore, having packaging templates in a dedicated `distro/pkg/` directory has following advantages as opposed to having them directly in `distro/`:

* `distro/` can contain arbitrary distro-related dirs as needed without affecting template discovery
* every `distro/pkg/*` dir is expected to be a valid packaging template - this makes discovery and management much easier in comparison to a case where some dirs are templates and some dirs are other unrelated things.

`distro/config/apkg.toml` (or similar) configuration file will be used to define/override project-specific behavior.


## output

All project-specific `apkg` **output** files should be placed into respective
subdirs in `pkg/` dir:

```
pkg
├── archives
│   ├── dev                  <- dev archives are created here
│   │   └── knot-resolver-5.1.3.1602777860.d5fc45b3.tar.xz
│   └── upstream             <- upstream archives (and signatures) are downloaded here
│       ├── knot-resolver-5.1.3.tar.xz
│       └── knot-resolver-5.1.3.tar.xz.asc
├── build
│   ├── pkgs                 <- package builds are done here - logs, artifacts, and other build outputs
│   │   ├── arch
│   │   ├── debian-10
│   │   └── fedora-33
│   └── srcpkgs              <- distro/pkg/$DISTRO/ files are converted to source packages here
│       ├── arch
│       ├── debian-10
│       └── fedora-33
├── pkgs                     <- successfully built packages are stored here
│   ├── arch
│   ├── debian-10
│   └── fedora-33
└── srcpkgs                  <- successfully built source packages are stored here
    ├── arch
    ├── debian-10
    └── fedora-33
```

this structure has following advantages:

* not spamming project root with temporary files
* each kind of file has a well-defined dedicated directory:
  * dev archive
  * upstream archive
  * source package build files
  * package build files
  * source packages
  * packages
* build files separated from build outputs
* build outputs separate for individual packages
* if build fails, user can just go to `pkg/build/*` and continue where `apkg` ended
* individual dirs or even entire `pkg/` can be safely deleted

Any successful `apkg` operation on a repo should result in a clean repo.

## packaging workflow overview

```

                                                    apkg packaging workflow


+--------------------------------------------------------+         +------------------------------------------------------------------+
|                                                        |         |                                                                  |
|     $ apkg make-archive                                |         |     $ apkg get-archive [1.2.3]                                   |
|                                                        |         |                                                                  |
|   in: repo at current commit                           |         |   in: version of upstream release                                |
|                                                        |         |                                                                  |
|  out: pkg/archives/dev/project*.tar.xz  (dev archive)  |         |  out: pkg/archives/upstream/project*.tar.xz  (upstream archive)  |
|                                                        |         |                                                                  |
+------------------------------------------+-------------+         +-------------+----------------------------------------------------+
                                           |                                     |
                                           |                                     |
                                           |                                     |
                                           v                                     v
                           +---------------+-------------------------------------+---------------+
                           |                                                                     |
                           |     $ apkg srcpkg                                                   |
                           |                                                                     |
                           |   in: distro/pkg/$PKGTEMPLATE/        (packaging template)          |
                           |       pkg/archives/*/project*.tar.xz  (archive)                     |
                           |                                                                     |
                           |  out: pkg/srcpkgs/$DISTRO/$SRCPKG         (source package)          |
                           |       pkg/build/srcpkgs/$DISTRO/$SRCPKG/  (build dir)               |
                           |                                                                     |
                           +----------------------------------+----------------------------------+
                                                              |
                                                              |
                                                              |
                                                              v
                               +------------------------------+-------------------------------+
                               |                                                              |
                               |     $ apkg build                                             |
                               |                                                              |
                               |   in: pkg/srcpkgs/$DISTRO/$SRCPKG  (source package)          |
                               |                                                              |
                               |  out: pkg/pkgs/$DISTRO/$PKG        (package)                 |
                               |       pkg/build/pkgs/$DISTRO/$PKG  (build dir)               |
                               |                                                              |
                               +--------------------------------------------------------------+
```

## initial goals

let's start with common packaging operations such as:


### make archive from repo

```
$> apkg make-archive [v1.2.3]
```
creates source archive from current (or specified) repo commit in `pkg/archives/dev/*`.


### get upstream archive

```
$> apkg get-archive [1.2.3]
```
downloads upstream archive for current commit (or specified version) into `pkg/archives/upstream/*` - requires archive URL configuration, supports signatures too. Such config can be stored in `distro/config/apkg.toml`

Both `make-archive` and `get-archive` (when configured) will be used by other commands when requested through parameters and might be useful to user on their own - better expose them properly.


### create source package

  * `package-*.src.rpm` for RPM-based systems such as Fedora, CentOS, SUSE, RHEL
  * `package_*.{dsc,debian.tar.xz,orig.tar.xz}` for Debian-based systems including Ubuntu and clones
  * `PKGBUILD` for Arch
  * in general whatever is needed to build a package somewhere

Detect current distro and build native source packages by default. In future, cross-build using VMs will probably be supported.

By default, create and use archive(tarball) from current repo commit but allow using remote and local archives as supported by `{make,get}-archive`.

Examples:

```
$> apkg srcpkg
```

* on `.deb`-based distro: `pkg/srcpkgs/debian-10/package_*.{dsc,debian.tar.xz,orig.tar.xz}`
* on `.rpm`-based distro: `pkg/srcpkgs/fedora-32/package-*.src.rpm`
* etc.

```
$> apkg srcpkg --archive ./pkg/archives/upstream/package-1.0.0.tgz
```
builds source package from specified local archive.

```
$> apkg srcpkg --archive https://some.page/archives/package-1.0.0.tgz
```
downloads specified archive and uses it to create source package.

```
$> apkg srcpkg --get-archive
```
downloads archive matching current repo commit from upstream (using `get-archive`) and creates source package from it. Requires configuration regarding archive URL.

```
$> apkg srcpkg --get-archive --version 1.2.3
```
downloads upstream archive version `1.2.3` (using `get-archive`), [switches `git` to version `1.2.3`?], and uses it to create source package.


### build a package from current commit locally

```
$> apkg build
```

Results in `pkg/pkgs/ubuntu-20.04/package_*.deb`  (depending on current distro)

Similar to `srcpkg` with extra step of local build.


### check current packaging status

```
$> apkg status
```

should print useful information about the state of packaging at current commit such as supported packaging types/distros, versions and whatever else will prove useful to packagers.
