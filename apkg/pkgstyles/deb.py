"""
This is 'deb' apkg package style for Debian-based distros such as
Debian, Ubuntu, and their many clones.
"""


SUPPORTED_DISTROS = [
    "ubuntu",
    "debian",
    "linuxmint",
    "raspbian",
    "scientific",
]


def is_valid_package_template(path):
    deb_files = ['rules', 'control', 'changelog']
    return all((path / f).exists() for f in deb_files)


def get_package_name(path):
    return "TODO-deb"
