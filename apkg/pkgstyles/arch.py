"""
This is 'arch' apkg package style for Arch linux
"""
import glob
from pathlib import Path
import os
import shutil

from apkg import exception
from apkg.log import getLogger, LOG_LEVEL, INFO
from apkg.compat import py35path
from apkg.util.run import cd, run


log = getLogger(__name__)


SUPPORTED_DISTROS = [
    'arch'
]


RE_PKG_NAME = r'pkgname\s*=\s*(\S+)'


def is_valid_template(path):
    pkgbuild = path / "PKGBUILD"
    return pkgbuild.exists()


def get_template_name(path):
    return _parse_pkgbuild(path / 'PKGBUILD', '$pkgname')


def get_srcpkg_nvr(path):
    return _parse_pkgbuild(path, '$pkgname-$pkgver-$pkgrel')


def _parse_pkgbuild(pkgbuild, bash):
    return run('bash', '-c', '. "%s" && echo "%s"'
               % (pkgbuild, bash), log_cmd=False)


def build_srcpkg(
        build_path,
        out_path,
        archive_path,
        template,
        env):
    in_pkgbuild = build_path / 'PKGBUILD'
    out_pkgbuild = out_path / 'PKGBUILD'
    log.info("building arch source package: %s" % in_pkgbuild)
    template.render(build_path, env or {})
    os.makedirs(out_path)
    log.info("copying PKGBUILD and archive to: %s" % out_path)
    shutil.copyfile(in_pkgbuild, out_pkgbuild)
    shutil.copyfile(archive_path, out_path / archive_path.name)
    return out_pkgbuild


def build_packages(
        build_path,
        out_path,
        srcpkg_path,
        **kwargs):
    if srcpkg_path.name != 'PKGBUILD':
        raise exception.InvalidSourcePackageFormat(
            fmt='arch source package format is PKGBUILD but got: %s'
            % srcpkg_path.name)
    log.info("copying source package to build dir: %s" % build_path)
    shutil.copytree(py35path(srcpkg_path.parent), py35path(build_path))
    # build package using makepkg
    log.info("starting arch package build using makepkg")
    with cd(build_path):
        run('makepkg', direct=bool(LOG_LEVEL <= INFO))
    log.info("copying built packages to result dir: %s" % out_path)
    os.makedirs(py35path(out_path), exist_ok=True)
    pkgs = []
    # find and copy resulting packages
    for src_pkg in glob.iglob('%s/*.zst' % build_path):
        dst_pkg = out_path / Path(src_pkg).name
        shutil.copyfile(py35path(src_pkg), py35path(dst_pkg))
        pkgs.append(dst_pkg)

    return pkgs


def install_build_deps(
        srcpkg_path,
        **kwargs):
    msg = ("build-dep installation isn't currently supported on arch\n\n"
           "this might work: makepkg -si && sudo pacman -R <package-name>")
    raise exception.DistroNotSupported(msg=msg)
