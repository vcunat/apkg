"""
apkg package style for RPM-based distros
such as Fedora, CentOS, SUSE, RHEL.

**source template**: `*.spec`

**source package:** `*.src.rpm`

**packages:** `*.rpm` built directly using `rpmbuild`
or `--isolated` using `mock`
"""
import glob
from pathlib import Path
import re
import subprocess

from apkg import ex
from apkg.log import getLogger
from apkg.util.run import run, sudo
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


SUPPORTED_DISTROS = [
    "fedora",
    "centos",
    "rhel",
    "oracle",
    "pidora",
    "opensuse",
    "scientific",
]


RE_PKG_NAME = r'Name:\s*(\S+)'
RE_BUILD_REQUIRES = r'BuildRequires:\s*(.*)'
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

    raise ex.ParsingFailed(
        msg="unable to determine Name from: %s" % spec)


def get_srcpkg_nvr(path):
    name = str(path.name)
    m = re.match(r'(.*)\.src.rpm', name)
    if m:
        return m.group(1)
    return name


def _get_package_manager(distro):
    default = 'dnf'
    if not distro:
        return default
    if distro.startswith('opensuse'):
        return 'zypper'
    m = re.match(r'(?:centos|rhel|oracle|scientific)-(\d+)', distro)
    if m and int(m.group(1)) <= 7:
        # use yum on EL <= 7
        return 'yum'
    return default


def build_srcpkg(
        build_path,
        out_path,
        archive_paths,
        template,
        env):
    rpmbuild_topdir = build_path / 'rpmbuild'
    rpmbuild_src = rpmbuild_topdir / 'SOURCES'
    rpmbuild_spec = rpmbuild_topdir / 'SPEC'

    rpmbuild_src.mkdir(parents=True, exist_ok=True)

    template.render(rpmbuild_src, env)

    spec_src_path = _get_spec(rpmbuild_src)
    spec_path = rpmbuild_spec / spec_src_path.name
    log.verbose("moving .spec file into SPEC: %s", spec_path)
    rpmbuild_spec.mkdir(exist_ok=True)
    spec_src_path.rename(spec_path)

    log.info("copying archive files into SOURCES: %s", rpmbuild_src)
    for src_path in archive_paths:
        dst_path = rpmbuild_src / src_path.name
        shutil.copyfile(src_path, dst_path)
    log.info("building .src.rpm using rpmbuild")
    out = run('rpmbuild', '-bs',
              '--define', '_topdir %s' % rpmbuild_topdir.resolve(),
              spec_path)

    log.info("copying .src.rpm to result dir: %s", out_path)
    out_path.mkdir(parents=True)
    srcpkgs = []
    for m in re.finditer(RE_RPMBUILD_OUT_SRPM, out):
        srpm = m.group(1)
        src_srpm = Path(srpm)
        dst_srpm = out_path / src_srpm.name
        shutil.copyfile(src_srpm, dst_srpm)
        srcpkgs.append(dst_srpm)
    if not srcpkgs:
        raise ex.ParsingFailed(
            msg="unable to parse rpmbuild results")
    return srcpkgs


def build_packages(
        build_path,
        out_path,
        srcpkg_paths,
        **kwargs):
    isolated = kwargs.get('isolated')
    pkgs = []
    srcpkg_path = srcpkg_paths[0]

    if isolated:
        log.info("starting isolated .rpm build using mock")
        # sudo shouldn't be necessary when in mock group
        # but apkg can't rely on that especially in containers etc.
        sudo('mock',
             '--resultdir', build_path,
             srcpkg_path,
             preserve_env=True,
             direct='auto')
        log.info("copying built packages to result dir: %s", out_path)
        out_path.mkdir(parents=True)
        for rpm in glob.iglob('%s/*.rpm' % build_path):
            src_pkg = Path(rpm)
            dst_pkg = out_path / src_pkg.name
            shutil.copyfile(src_pkg, dst_pkg)
            pkgs.append(dst_pkg)
    else:
        log.info("starting direct host .rpm build using rpmbuild")
        rpmbuild_topdir = build_path / 'rpmbuild'
        rpmbuild_topdir.mkdir(parents=True, exist_ok=True)
        out = run('rpmbuild', '--rebuild',
                  '--define', '_topdir %s' % rpmbuild_topdir.resolve(),
                  srcpkg_path)
        log.info("copying built packages to result dir: %s", out_path)
        out_path.mkdir(parents=True)
        for m in re.finditer(RE_RPMBUILD_OUT_RPM, out):
            rpm = m.group(1)
            src_pkg = Path(rpm)
            dst_pkg = out_path / src_pkg.name
            shutil.copyfile(src_pkg, dst_pkg)
            pkgs.append(dst_pkg)
        if not pkgs:
            raise ex.ParsingFailed(
                msg="unable to parse rpmbuild results")

    return pkgs


def get_build_deps(srcpkg_path):
    """
    parse BuildRequires out of .src.rpm
    """
    cmd = "rpm2cpio '%s' | cpio -i --to-stdout '*.spec'" % srcpkg_path
    out = subprocess.getoutput(cmd)
    return re.findall(RE_BUILD_REQUIRES, out)


def install_build_deps(
        srcpkg_path,
        **kwargs):
    interactive = kwargs.get('interactive', False)
    distro = kwargs.get('distro')
    pm = _get_package_manager(distro)
    if pm == 'dnf':
        cmd = ['dnf', 'builddep', '--srpm']
        if not interactive:
            cmd.append('-y')
        cmd.append(srcpkg_path.resolve())
    else:
        deps = get_build_deps(srcpkg_path)
        cmd = [pm, 'install']
        if not interactive:
            cmd.append('-y')
        cmd += deps

    log.info("installing build deps using %s", cmd[0])
    sudo(*cmd, direct=True)


def install_custom_packages(
        packages,
        **kwargs):
    interactive = kwargs.get('interactive', False)
    distro = kwargs.get('distro')
    pm = _get_package_manager(distro)

    cmd = [pm, 'install']
    if not interactive:
        cmd += ['-y']
    cmd += packages
    sudo(*cmd, direct=True)


def install_distro_packages(
        packages,
        **kwargs):
    # dnf handles both local and distro packages
    install_custom_packages(packages, **kwargs)
