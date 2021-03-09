"""
apkg package style for RPM-based distros
such as Fedora, CentOS, SUSE, RHEL.

**source template**: `*.spec`

**source package:** `*.src.rpm`

**packages:** `*.rpm` built directly using `rpmbuild`
or `--isolated` using `mock`
"""
import glob
import os
from pathlib import Path
import re
import shutil

from apkg.compat import py35path
from apkg import exception
from apkg.log import getLogger, LOG_LEVEL, INFO
from apkg.util.run import cd, run, sudo


log = getLogger(__name__)


SUPPORTED_DISTROS = [
    "fedora",
    "centos",
    "rhel",
    "oracle",
    "pidora",
    "scientific",
]


RE_PKG_NAME = r'Name:\s*(\S+)'
RE_RPMBUILD_OUT_RPM = r'Wrote:\s+(.*\.rpm)\s*'
RE_RPMBUILD_OUT_SRPM = r'Wrote:\s+(.*\.src.rpm)\s*'


def _get_spec(path):
    for s in glob.iglob("%s/*.spec" % path):
        return Path(s)
    return None


def is_valid_template(path):
    return bool(_get_spec(path))


def get_template_name(path):
    spec = _get_spec(path)

    for line in spec.open():
        m = re.match(RE_PKG_NAME, line)
        if m:
            return m.group(1)

    raise exception.ParsingFailed(
        msg="unable to determine Name from: %s" % spec)


def get_srcpkg_nvr(path):
    name = str(path.name)
    m = re.match(r'(.*)\.src.rpm', name)
    if m:
        return m.group(1)
    return name


def _get_dnf_or_yum(distro):
    tool = 'dnf'
    if not distro:
        return tool
    m = re.match(r'(?:centos|rhel|oracle|scientific)-(\d+)', distro)
    if m and int(m.group(1)) <= 7:
        # use yum on centos <= 7
        tool = 'yum'
    return tool


def build_srcpkg(
        build_path,
        out_path,
        archive_path,
        template,
        env):
    rpmbuild_path = Path.home() / 'rpmbuild'
    rpmbuild_ar_path = rpmbuild_path / 'SOURCES' / archive_path.name

    template.render(build_path, env)
    spec_path = _get_spec(build_path)
    log.verbose(".spec file: %s", spec_path)
    log.info("copying archive into build dir: %s", archive_path)
    os.makedirs(py35path(rpmbuild_ar_path.parent), exist_ok=True)
    shutil.copyfile(py35path(archive_path), py35path(rpmbuild_ar_path))
    log.info("building .src.rpm using rpmbuild")
    with cd(build_path):
        out = run('rpmbuild', '-bs', spec_path.name)

    log.info("copying .src.rpm to result dir: %s", out_path)
    os.makedirs(py35path(out_path))
    srcpkgs = []
    for m in re.finditer(RE_RPMBUILD_OUT_SRPM, out):
        srpm = m.group(1)
        src_srpm = Path(srpm)
        dst_srpm = out_path / src_srpm.name
        shutil.copyfile(py35path(src_srpm), py35path(dst_srpm))
        srcpkgs.append(dst_srpm)
    if not srcpkgs:
        raise exception.ParsingFailed(
            msg="unable to parse rpmbuild results")
    return srcpkgs


def build_packages(
        build_path,
        out_path,
        srcpkg_path,
        **kwargs):
    isolated = kwargs.get('isolated')
    direct_run = bool(LOG_LEVEL <= INFO)
    pkgs = []
    os.makedirs(py35path(build_path))

    if isolated:
        log.info("starting isolated .rpm build using mock")
        # sudo shouldn't be necessary when in mock group
        # but apkg can't rely on that especially in containers etc.
        sudo('mock',
             '--resultdir', build_path,
             srcpkg_path,
             preserve_env=True,
             direct=direct_run)
        log.info("copying built packages to result dir: %s", out_path)
        os.makedirs(py35path(out_path))
        for rpm in glob.iglob('%s/*.rpm' % build_path):
            src_pkg = Path(rpm)
            dst_pkg = out_path / src_pkg.name
            shutil.copyfile(py35path(src_pkg), py35path(dst_pkg))
            pkgs.append(dst_pkg)
    else:
        log.info("starting direct .rpm build using rpmbuild")
        srcpkg_path_abs = srcpkg_path.resolve()
        with cd(build_path):
            out = run('rpmbuild', '--rebuild',
                      srcpkg_path_abs)
        log.info("copying built packages to result dir: %s", out_path)
        os.makedirs(py35path(out_path))
        for m in re.finditer(RE_RPMBUILD_OUT_RPM, out):
            rpm = m.group(1)
            src_pkg = Path(rpm)
            dst_pkg = out_path / src_pkg.name
            shutil.copyfile(py35path(src_pkg), py35path(dst_pkg))
            pkgs.append(dst_pkg)
        if not pkgs:
            raise exception.ParsingFailed(
                msg="unable to parse rpmbuild results")

    return pkgs


def install_build_deps(
        srcpkg_path,
        **kwargs):
    interactive = kwargs.get('interactive', False)
    distro = kwargs.get('distro')
    tool = _get_dnf_or_yum(distro)
    if tool == 'yum':
        cmd = ['yum-builddep']
    else:
        cmd = ['dnf', 'builddep', '--srpm']
    log.info("installing build deps using %s", cmd[0])
    if not interactive:
        cmd.append('-y')
    cmd.append(srcpkg_path.resolve())
    sudo(*cmd, direct=True)
