# apkg config

`apkg` looks for config file `distro/config/apkg.toml`.

Please see {{ 'distro/config/apkg.toml' | file_link }} for up-to-date example.


## [project]

The primary config section containing project-specific settings.

### project.name

By default, project name is guessed from project dir name but that can break
easily when the project dir is renamed so it's better to specify it explicitly
in using `project.name`

```
[project]
name = "banana"
```

This is available to templates through {% raw %}`{{ project.name }}`{% endraw %}.

### project.make_archive_script

In order to create packages from your project source, `apkg` requires a script
which creates archive from current project state.

The script MUST return the path to created archive on last line of its
`stdout`.

Include such script in your project and then point to it using `make_archive_script`:

```
[project]
make_archive_script = "scripts/make-dev-archive.sh"
```

script example: {{ 'scripts/make-dev-archive.sh' | file_link  }}

## [upstream]

Config section related to project upstream settings.

### upstream.archive_url

To easily download upstream archives using `apkg` you can specify
`upstream.archive_url` with [templating](templates.md) available including
special `version` variable:

{% raw %}
```
[upstream]
archive_url = "https://banana.proj/dl/{{ project.name }}/{{ project.name }}-{{ version }}.tar.xz"
```
{% endraw %}

### upstream.signature_url

Optional signature file to download alongside upstream archive.

### upstream.version_script

If default upstream version auto-detection from HTML listing of files at
`upstream.archive_url` parent doesn't work for your project or you want full
control over the process, you can create a custom executable script which
prints current upstream version as a last line of its stdout and tell `apkg`
to use it with `upstream.version_script` option:

```
[upstream]
version_script = "scripts/upstream-version.py"
```

This option overrides default auto-detection mechanism.

script example: {{ 'scripts/upstream-version.py' | file_link  }}
