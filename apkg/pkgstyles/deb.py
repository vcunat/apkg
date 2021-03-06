"""
apkg package style for **Debian**
and its many clones such as Ubuntu or Mint.

**source template**: content of `debian/` dir (`control`, `changelog`, ...)

**source package:** `*.dsc` + archives

**packages:** `*.deb`

**required distro packages**:

 * core: `devscripts`
 * isolated build: `pbuilder`
"""
import glob
import os
from pathlib import Path
import re
import sys
import tempfile

from apkg import ex
from apkg.log import getLogger
from apkg import parse
from apkg import pkgtemplate
from apkg.util.run import cd, run, sudo
from apkg.util.archive import unpack_archive
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


SUPPORTED_DISTROS = [
    "ubuntu",
    "debian",
    "linuxmint",
    "raspbian",
]
DISTRO_REQUIRES = {
    'core': ['devscripts'],
    'isolated': ['pbuilder'],
}


RE_PKG_NAME = r'Source:\s*(\S+)'
# orbital regexp cannon to parse Build-Depends from debian/control
RE_BUILD_DEPENDS = (
    r'(?:\n|\A)Build-Depends(?:-Indep)?:[ \t]*'  # no whitespace before
    r'(?:\n[ \t]+)?'  # optional leading newline with whitespace
    r'((?:[^,\n]+)'   # first build dep
    r'(?:,(?:[ \t]*'  # comma separator and optional whitespace
    r'(?:\n[ \t]+)?'  # optional newline starting with whitespace
    r'[^,\n]+))*)'    # 0-N other build deps
)


def is_valid_template(path):
    deb_files = ['rules', 'control', 'changelog']
    return all((path / f).exists() for f in deb_files)


def get_template_name(path):
    control = path / 'control'

    for line in control.open():
        m = re.match(RE_PKG_NAME, line)
        if m:
            return m.group(1)

    raise ex.ParsingFailed(
        msg="unable to determine Source from: %s" % control)


def get_srcpkg_nvr(path):
    nvr, _, _ = str(path.name).rpartition('.')
    return nvr


def copy_srcpkg_files(src_path, dst_path):
    # not part of pkgstyle interface yet but probably should be
    for pattern in [
            '*.dsc',
            '*_source.*',  # questionable, some tools need these
            '*.debian.tar.*',
            '*.orig.tar.*',
            '*.diff.*']:
        for f in glob.iglob('%s/%s' % (src_path, pattern)):
            srcp = Path(f)
            shutil.copyfile(f, dst_path / srcp.name)


def build_srcpkg(
        build_path,
        out_path,
        archive_paths,
        template,
        env):
    """
    build debian source package
    """
    archive_path = archive_paths[0]
    nv, _ = parse.split_archive_ext(archive_path.name)
    log.info("building deb source package: %s", nv)
    log.info("unpacking archive: %s", archive_path)
    source_path = unpack_archive(archive_path, build_path)
    log.verbose("source package root dir: %s", source_path)
    if not source_path or not source_path.exists():
        msg = "archive unpack didn't result in expected dir: %s" % source_path
        raise ex.UnexpectedCommandOutput(msg=msg)
    # render template
    debian_path = source_path / 'debian'
    template.render(debian_path, env)
    # copy archive with debian .orig name
    _, _, _, ext = parse.split_archive_fn(archive_path.name)
    debian_ar = "%s_%s.orig%s" % (env['name'], env['version'], ext)
    debian_ar_path = build_path / debian_ar
    log.info("copying archive into source package: %s", debian_ar_path)
    shutil.copyfile(archive_path, debian_ar_path)

    log.info("building deb source-only package...")
    with cd(source_path):
        run('dpkg-buildpackage',
            '-S',   # source-only, no binary files
            '-sa',  # source includes orig, always
            '-d',   # do not check build dependencies and conflicts
            '-nc',  # do not pre clean source tree
            '-us',  # unsigned source package.
            '-uc',  # unsigned .changes file.
            direct='auto')

    log.info("copying source package to result dir: %s", out_path)
    out_path.mkdir(parents=True)
    copy_srcpkg_files(build_path, out_path)
    fns = glob.glob('%s/*' % out_path)
    # make sure .dsc is first
    for i, fn in enumerate(fns):
        if fn.endswith('.dsc'):
            fns = [fns.pop(i)] + fns
            break
    else:
        raise ex.UnexpectedCommandOutput(
            msg="no *.dsc found after moving built source package")
    return list(map(Path, fns))


def build_packages(
        build_path,
        out_path,
        srcpkg_paths,
        **kwargs):
    """
    build .deb packages from source package
    """
    srcpkg_path = srcpkg_paths[0]
    build_path.mkdir(parents=True)
    out_path.mkdir(parents=True)
    isolated = kwargs.get('isolated')
    if isolated:
        log.info("starting isolated build using pbuilder")
        # TODO: ensure pbuilder's base image exists (pbuilder create)
        sudo('pbuilder', 'build',
             '--buildresult', build_path,
             srcpkg_path,
             preserve_env=True,  # preserve env inc. DEB_BUILD_OPTIONS
             direct='auto')
    else:
        # unpack source package
        log.info("unpacking source package for direct host build")
        srcpkg_abspath = srcpkg_path.resolve()
        with cd(build_path):
            run('dpkg-source', '-x', srcpkg_abspath,
                direct='auto')
        # find unpacked source dir
        try:
            source_glob = '%s/*/' % build_path
            source_path = Path(glob.glob(source_glob)[0])
        except IndexError:
            msg = "failed to find unpacked source dir: %s"
            raise ex.UnexpectedCommandOutput(msg % source_glob)

        log.info("starting direct host build using dpkg-buildpackage")
        with cd(source_path):
            # build
            run('dpkg-buildpackage',
                '-us',  # unsigned source package.
                '-uc',  # unsigned .changes file.
                direct='auto')

    pkgs = []
    log.info("copying built packages to result dir: %s", out_path)
    for src_pkg in glob.iglob('%s/*.deb' % build_path):
        dst_pkg = out_path / Path(src_pkg).name
        shutil.copyfile(src_pkg, dst_pkg)
        pkgs.append(dst_pkg)

    return pkgs


def install_distro_packages(
        packages,
        **kwargs):
    interactive = kwargs.get('interactive', False)

    cmd = ['apt-get', 'install']
    env = os.environ.copy()
    if not interactive:
        env['DEBIAN_FRONTEND'] = 'noninteractive'
        cmd += ['-y']

    cmd += packages
    sudo(*cmd, env=env, direct=True)


def install_custom_packages(
        packages,
        **kwargs):

    def local_path(pkg):
        """
        apt-get is able to install local packages
        as long as they use full path or relative including ./
        """
        p = str(pkg)
        if p[0] not in '/\\.':
            return "./%s" % p
        return p

    interactive = kwargs.get('interactive', False)

    cmd = ['apt-get', 'install']
    env = os.environ.copy()
    if not interactive:
        env['DEBIAN_FRONTEND'] = 'noninteractive'
        cmd += ['-y']

    cmd += list(map(local_path, packages))
    sudo(*cmd, env=env, direct=True)


def install_build_deps(
        deps,
        **kwargs):
    """
    install debian build deps

    Debian Build-Depends can contain strings not handled by
    `apt-get install` such as "(>= 9~)"

    New `apt-get satisfy` command handles Build-Depends strings fine
    but it isn't available on current.

    Try to use `apt-get satisfy` if available,
    otherwise revert to stripping special strings and use `install`.
    """
    interactive = kwargs.get('interactive', False)

    if has_aptget_satisfy_():
        # unlike install, satisfy can handle versioned deps
        cmd = ['apt-get', 'satisfy']
        env = os.environ.copy()
        if not interactive:
            env['DEBIAN_FRONTEND'] = 'noninteractive'
            cmd += ['-y']
        cmd += deps
        sudo(*cmd, env=env, direct=True)
    else:
        # satisfy not available, strip special strings and use install
        packages = [strip_dep_(d) for d in deps]
        install_distro_packages(packages, **kwargs)


def get_build_deps_from_template(
        template_path,
        **kwargs):
    """
    parse Build-Depends from packaging template
    """
    distro = kwargs.get('distro')
    # render control file
    this_style = sys.modules[__name__]
    t = pkgtemplate.PackageTemplate(template_path, style=this_style)
    env = pkgtemplate.DUMMY_ENV.copy()
    if distro:
        env['distro'] = distro
    control_text = t.render_file_content('control', env=env)
    return get_build_deps_from_control_(control_text)


def get_build_deps_from_srcpkg(
        srcpkg_path,
        **_):
    """
    parse Build-Depends from source package
    """
    debar_path = get_srcpkg_debian_archive_(srcpkg_path.parent)
    log.info("unpacking debian archive: %s", debar_path)
    with tempfile.TemporaryDirectory(prefix='apkg_deb_') as td:
        unpack_path = unpack_archive(debar_path, td)
        control_path = unpack_path / 'control'
        control_text = control_path.open().read()
    return get_build_deps_from_control_(control_text)


# functions bellow with _ postfix are specific to this pkgstyle


def get_build_deps_from_control_(control_text):
    """
    parse Build-Depends from debian control file contents
    """
    m = re.findall(RE_BUILD_DEPENDS, control_text)
    if not m:
        msg = "unable to parse Build-Depends from control"
        raise ex.ParsingFailed(msg=msg)
    deps = []
    for deps_raw in m:
        deps += re.split(r'\s*,\s*', deps_raw)
    return deps


def get_srcpkg_debian_archive_(path):
    ars = glob.glob('%s/*.debian.tar.?z' % path)
    if not ars:
        msg = "unable to find debian archive in srcpkg: %s" % path
        raise ex.InvalidInput(msg=msg)
    if len(ars) > 1:
        msg = "multiple debian archives found in srcpkg: %s" % path
        raise ex.InvalidInput(msg=msg)
    return ars[0]


def has_aptget_satisfy_():
    """
    is `apt-get satisfy` command available?
    """
    o = run('apt-get', '-h', log_cmd=False, fatal=False)
    return 'satisfy' in o


def strip_dep_(dep):
    """
    strip special version strings (as found in Build-Depends)
    in order for dep to be installable through `apt-get install`
    """
    return re.split(r'[\s\[\(]', dep)[0]
