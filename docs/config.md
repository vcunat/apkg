# apkg config

## project config

`apkg` looks for project config file `distro/config/apkg.toml`.

Please see {{ 'distro/config/apkg.toml' | file_link }} for up-to-date example.

Currently, all options belong under `[project]` section:


### project.name

By default, project name is guessed from project dir name but that can break easily when the project dir is renamed so it's better to specify it explicitly in using `name`

```
[project]
name = "banana"
```

This is available to templates through {% raw %}`{{ project.name }}`{% endraw %}.


### project.make_archive_script

In order to create packages from your project source, `apkg` requires a script which creates archive from current project state.

The script MUST return the path to created archive on last line of its `stdout`.

Include such script in your project and then point to it using `make_archive_script`:

```
[project]
make_archive_script = "scripts/make-dev-archive.sh"
```


### project.upstream_archive_url

To easily download upstream archives using `apkg` you can specify `upstream_archive_url` with templating available:

{% raw %}
```
[project]
upstream_archive_url = "https://banana.proj/dl/{{ project.name }}/{{ project.name }}-{{ version }}.tar.xz"
```
{% endraw %}
