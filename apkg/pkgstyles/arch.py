"""
This is 'arch' apkg package style for Arch linux
"""
import re
import shutil


SUPPORTED_DISTROS = [
    'arch'
]


RE_PKG_NAME = r'pkgname\s*=\s*(\S+)'


def is_valid_package_template(path):
    pkgbuild = path / "PKGBUILD"
    return pkgbuild.exists()


def get_package_name(path):
    pkgbuild = path / "PKGBUILD"

    for line in pkgbuild.open():
        m = re.match(RE_PKG_NAME, line)
        if m:
            return m.group(1)

    raise exception.ParsingFailed(
            msg="unable to determine pkgname from: %s" % pkgbuild)


def build_source_package(build_path, archive_path, vars={}):
    shutil.copyfile(archive_path, build_path / archive_path.name)
