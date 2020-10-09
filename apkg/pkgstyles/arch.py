"""
This is 'arch' apkg packaging style for Arch linux
"""


SUPPORTED_DISTROS = [
    'arch'
]


def is_valid_packaging_template(path):
    pkgbuild = path / "PKGBUILD"
    return pkgbuild.exists()
