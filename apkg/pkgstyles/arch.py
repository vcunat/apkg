"""
apkg package style for **Arch** linux.

**source template:** `PKGBUILD`

**source package:** `PKGBUILD`

**packages:** `*.zst` built using `makepkg`
"""
import glob
from pathlib import Path

from apkg import ex
from apkg.log import getLogger
from apkg.util.run import cd, run, sudo
import apkg.util.shutil35 as shutil


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
        archive_paths,
        template,
        env):
    archive_path = archive_paths[0]
    in_pkgbuild = build_path / 'PKGBUILD'
    out_pkgbuild = out_path / 'PKGBUILD'
    out_archive = out_path / archive_path.name
    log.info("building arch source package: %s", in_pkgbuild)
    template.render(build_path, env or {})
    out_path.mkdir(parents=True)
    log.info("copying PKGBUILD and archive to: %s", out_path)
    shutil.copyfile(in_pkgbuild, out_pkgbuild)
    shutil.copyfile(archive_path, out_archive)
    return [out_pkgbuild, out_archive]


def build_packages(
        build_path,
        out_path,
        srcpkg_paths,
        **kwargs):
    srcpkg_path = srcpkg_paths[0]
    if srcpkg_path.name != 'PKGBUILD':
        raise ex.InvalidSourcePackageFormat(
            fmt="arch source package format is PKGBUILD but got: %s"
            % srcpkg_path.name)
    isolated = kwargs.get('isolated')
    log.info("copying source package to build dir: %s", build_path)
    shutil.copytree(srcpkg_path.parent, build_path)
    # build package using makepkg
    if not isolated:
        msg = "arch doesn't support direct host build - using isolated"
        log.warning(msg)
    log.info("starting isolated arch package build using makepkg")
    with cd(build_path):
        run('makepkg', direct='auto')
    log.info("copying built packages to result dir: %s", out_path)
    out_path.mkdir(parents=True, exist_ok=True)
    pkgs = []
    # find and copy resulting packages
    for src_pkg in glob.iglob('%s/*.zst' % build_path):
        dst_pkg = out_path / Path(src_pkg).name
        shutil.copyfile(src_pkg, dst_pkg)
        pkgs.append(dst_pkg)

    return pkgs


def install_custom_packages(
        packages,
        **kwargs):
    interactive = kwargs.get('interactive', False)
    cmd = ['pacman', '-U']
    if not interactive:
        cmd += ['--noconfirm']
    cmd += packages
    sudo(*cmd, direct=True)


def install_distro_packages(
        packages,
        **kwargs):
    interactive = kwargs.get('interactive', False)
    cmd = ['pacman', '-S']
    if not interactive:
        cmd += ['--noconfirm']
    cmd += packages
    sudo(*cmd, direct=True)
