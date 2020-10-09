"""
This is 'deb' apkg packaging style for Debian-based distros such as
Debian, Ubuntu, and their many clones.
"""


SUPPORTED_DISTROS = [
    "ubuntu",
    "debian",
    "linuxmint",
    "raspbian",
    "scientific",
]


def is_valid_packaging_template(path):
    deb_files = ['rules', 'control', 'changelog']
    return all((path / f).exists() for f in deb_files)
