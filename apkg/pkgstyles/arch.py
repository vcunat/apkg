"""
This is 'arch' apkg package style for Arch linux
"""
import os
import re
import shutil

from apkg import exception
from apkg import log


SUPPORTED_DISTROS = [
    'arch'
]


RE_PKG_NAME = r'pkgname\s*=\s*(\S+)'


def is_valid_template(path):
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


def build_srcpkg(
        build_path,
        out_path,
        archive_path,
        template,
        env):
    in_pkgbuild = build_path / 'PKGBUILD'
    log.info("building arch source package: %s" % in_pkgbuild)
    template.render(build_path, env or {})
    os.makedirs(out_path)
    log.info("copying PKGBUILD and archive to: %s" % out_path)
    shutil.copyfile(in_pkgbuild, out_path / 'PKGBUILD')
    shutil.copyfile(archive_path, out_path / archive_path.name)
