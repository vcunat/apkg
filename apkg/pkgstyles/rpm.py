"""
apkg package style for RPM-based distros
such as Fedora, CentOS, SUSE, RHEL.

!!! warning
    `rpm` pkgstyle **isn't finished yet**! it will be done for v0.1

**source template**: `*.spec`

!!! TODO
    **source package:** `*.src.rpm`

!!! TODO
    **packages:** `*.rpm` built directly using `rpmbuild`
    or `--isolated` using `mock`
"""
import glob


SUPPORTED_DISTROS = [
    "fedora",
    "centos",
    "rhel",
    "sles",
    "opensuse",
    "oracle",
    "pidora",
    "scientific",
]


def is_valid_template(path):
    for _ in glob.iglob("%s/*.spec" % path):
        return True
    return False


def get_package_name(path):
    return "TODO: rpm @ %s" % path
