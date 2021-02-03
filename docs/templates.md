# apkg package templates

In order to be able to maintain packages for a families of distros using same [packaging style](pkgstyles.md) `apkg` supports templating through [jinja](https://jinja.palletsprojects.com/en/2.11.x/).

Individual directories in `distro/pkg/` are considered to be **package templates** each using a particular [packaging style](pkgstyles.md) which is determined automatically by `apkg` based on files present in a template.

{% raw %}
Version string should be replaced with `{{ version }}` macro in relevant
files and such templating is available for all files present in a template -
you can reference ``{{ project.name }}`` and more.
{% endraw %}

!!! TODO
    package template documentation is **Work in Progress**, please refer to `apkg` templates for now:

    * `arch` template: {{ 'distro/pkg/arch' | file_link }}
    * `deb` template: {{ 'distro/pkg/deb' | file_link }}

## import existing packaging

To import existing packaging sources as `apkg` templates simply copy copy
them into a new template dir and change all occurrences of version string with
`{{ version }}`.

{% raw %}
### import debian-based packaging

``` bash
cp r ~/debpkg/debian pkg/distro/deb
# change version in latest changelog entry to {{ version }}
edit pkg/distro/deb/changelog
```

### import rpm packaging

``` bash
cp -r ~/rpmpkg pkg/distro/rpm
# change .spec Version to {{ version }}
edit pkg/distro/rpm/rpmpkg.spec
```
{% endraw %}
