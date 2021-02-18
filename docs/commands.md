# apkg commands

To get a summary of available `apkg` commands, simply run it without parameters:

``` text
$> apkg

{{ 'apkg.cli' | mod_doc }}
```

Use `--help`/`-h` after a command to get help for that particular command instead:

``` text
$> apkg command -h
```

## status

{{ 'status' | cmd_help }}

Example:

``` text
$> apkg status

project name:            apkg
project base path:       /home/u/src/apkg
project VCS:             git
project config:          distro/config/apkg.toml (exists)
package templates path:  distro/pkg (exists)
package templates:
    arch: distro/pkg/arch
    deb: distro/pkg/deb
    rpm: distro/pkg/rpm

current distro: arch / Arch Linux
    package style: arch
    package template: distro/pkg/arch
```

## make-archive

{{ 'make-archive' | cmd_help }}

`make-archive` requires
[project.make_archive_script](config.md#projectmake_archive_script)
config option to be set.

This command will only succeed when the script finishes successfully (with
exit code 0) and the resulting archive it created and printed to stdout
followed by one line for each additional file (like signature).

Resulting archive is copied to `pkg/archives/dev/` or to `--result-dir`.


## get-archive

{{ 'get-archive' | cmd_help }}

`get-archive` requires
[upstream.archive_url](config.md#upstreamarchive_url)
config option to be set with additional options available in
[upstream config section](config.md#upstream)

This command will only succeed when it managed to download specified archive.

Archive is downloaded into `pkg/archives/upstream/` or to `--result-dir`.

If automatic latest upstream version detection doesn't work,
you can always supply version manually with `-v`/`--version` option,
i.e. `apkg get-archive -v 1.2.3`


## srcpkg

{{ 'srcpkg' | cmd_help }}

!!! TODO
    this and all following commands require proper explanation

## build

{{ 'build' | cmd_help }}


## build-dep

{{ 'build-dep' | cmd_help }}
