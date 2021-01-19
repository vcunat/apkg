"""
This is 'deb' apkg package style for Debian-based distros such as
Debian, Ubuntu, and their many clones.
"""
import glob
import os
from pathlib import Path
import re
import shutil

from apkg.compat import py35path
from apkg import exception
from apkg import log
from apkg import parse
from apkg.util.run import cd, run, sudo


SUPPORTED_DISTROS = [
    "ubuntu",
    "debian",
    "linuxmint",
    "raspbian",
]


RE_PKG_NAME = r'Source:\s*(\S+)'


def is_valid_template(path):
    deb_files = ['rules', 'control', 'changelog']
    return all((path / f).exists() for f in deb_files)


def get_template_name(path):
    control = path / 'control'

    for line in control.open():
        m = re.match(RE_PKG_NAME, line)
        if m:
            return m.group(1)

    raise exception.ParsingFailed(
            msg="unable to determine Source from: %s" % control)


def get_srcpkg_nvr(path):
    nvr, _, _ = str(path.name).rpartition('.')
    return nvr


def _copy_srcpkg_files(src_path, dst_path):
    for pattern in ['*.dsc', '*.debian.tar.*', '*.orig.tar.*', '*.diff.*']:
        for f in glob.iglob('%s/%s' % (src_path, pattern)):
            srcp = Path(f)
            shutil.copyfile(py35path(f), py35path(dst_path / srcp.name))


# pylint: disable=too-many-locals
def build_srcpkg(
        build_path,
        out_path,
        archive_path,
        template,
        env):
    nv = "%s-%s" % (env['name'], env['version'])
    source_path = build_path / nv
    log.info("building deb source package: %s" % nv)
    log.info("unpacking archive: %s" % archive_path)
    os.makedirs(py35path(source_path))
    run('aunpack', '-X', build_path, archive_path)
    if not source_path.exists():
        # NOTE: if this happens oftern (it shouldn't), consider using
        #       atool's --save-outdir option above
        msg = "archive unpack didn't result in expected dir: %s" % source_path
        raise exception.UnexpectedCommandOutput(msg=msg)
    # render template
    debian_path = source_path / 'debian'
    template.render(debian_path, env)
    # copy archive with debian .orig name
    _, _, _, ext = parse.split_archive_fn(archive_path.name)
    debian_ar = "%s_%s.orig%s" % (env['name'], env['version'], ext)
    debian_ar_path = build_path / debian_ar
    log.info("copying archive into source package: %s", debian_ar_path)
    shutil.copyfile(py35path(archive_path), py35path(debian_ar_path))

    log.info("building deb source-only package...")
    direct = bool(log.log.level <= log.INFO)
    with cd(source_path):
        run('dpkg-buildpackage',
            '-S',   # source-only, no binary files
            '-sa',  # source includes orig, always
            '-d',   # do not check build dependencies and conflicts
            '-nc',  # do not pre clean source tree
            '-us',  # unsigned source package.
            '-uc',  # unsigned .changes file.
            direct=direct)

    log.info("copying source package to result dir: %s", out_path)
    os.makedirs(py35path(out_path))
    _copy_srcpkg_files(build_path, out_path)
    try:
        return Path(glob.glob('%s/*.dsc' % out_path)[0])
    except KeyError:
        raise exception.UnexpectedCommandOutput(
            msg="no *.dsc found after moving built source package")


def build_packages(
        build_path,
        out_path,
        srcpkg_path,
        **kwargs):
    os.makedirs(py35path(build_path))
    os.makedirs(py35path(out_path))
    isolated = kwargs.get('isolated')
    if isolated:
        log.info("starting isolated build using pbuilder")
        # TODO: ensure pbuilder's base image exists (pbuilder create)
        sudo('pbuilder', 'build',
             '--buildresult', build_path,
             srcpkg_path,
             preserve_env=True,  # preserve env inc. DEB_BUILD_OPTIONS
             direct=True)
    else:
        nvr, _ = os.path.splitext(py35path(srcpkg_path.name))
        nv, _, _ = nvr.rpartition('-')
        # unpack source package
        log.info("unpacking source package for direct build")
        srcpkg_abspath = srcpkg_path.resolve()
        with cd(build_path):
            run('dpkg-source', '-x', srcpkg_abspath,
                log_cmd=False)
        # find unpacked source dir
        try:
            source_glob = '%s/*/' % build_path
            source_path = Path(glob.glob(source_glob)[0])
        except IndexError:
            msg = "failed to find unpacked source dir: %s"
            raise exception.UnexpectedCommandOutput(msg % source_glob)

        log.info("starting direct build using dpkg-buildpackage")
        with cd(source_path):
            # build
            run('dpkg-buildpackage',
                '-us',  # unsigned source package.
                '-uc',  # unsigned .changes file.
                direct=True)

    pkgs = []
    log.info("copying built packages to result dir: %s" % out_path)
    for src_pkg in glob.iglob('%s/*.deb' % build_path):
        dst_pkg = out_path / Path(src_pkg).name
        shutil.copyfile(py35path(src_pkg), py35path(dst_pkg))
        pkgs.append(dst_pkg)

    return pkgs


def install_build_deps(
        srcpkg_path,
        **kwargs):
    interactive = kwargs.get('interactive', False)
    log.info("installing build deps using apt-get build-dep")
    cmd = ['apt-get', 'build-dep']
    if not interactive:
        cmd.append('-y')
    cmd.append(srcpkg_path.resolve())
    sudo(*cmd, direct=True)
