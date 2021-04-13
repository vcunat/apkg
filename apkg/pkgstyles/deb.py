"""
apkg package style for **Debian**
and its many clones such as Ubuntu or Mint.

**source template**: content of `debian/` dir (`control`, `changelog`, ...)

**source package:** `*.dsc` + archives

**packages:** `*.deb` built directly using `dpkg-buildpackage`
or `--isolated` using `pbuilder`
"""
import glob
from pathlib import Path
import re

from apkg import ex
from apkg.log import getLogger
from apkg import parse
from apkg.util.run import cd, run, sudo
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


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

    raise ex.ParsingFailed(
        msg="unable to determine Source from: %s" % control)


def get_srcpkg_nvr(path):
    nvr, _, _ = str(path.name).rpartition('.')
    return nvr


def _copy_srcpkg_files(src_path, dst_path):
    for pattern in [
            '*.dsc',
            '*_source.*',
            '*.debian.tar.*',
            '*.orig.tar.*',
            '*.diff.*']:
        for f in glob.iglob('%s/%s' % (src_path, pattern)):
            srcp = Path(f)
            shutil.copyfile(f, dst_path / srcp.name)


# pylint: disable=too-many-locals
def build_srcpkg(
        build_path,
        out_path,
        archive_paths,
        template,
        env):
    archive_path = archive_paths[0]
    nv, _ = parse.split_archive_ext(archive_path.name)
    source_path = build_path / nv
    log.info("building deb source package: %s", nv)
    log.info("unpacking archive: %s", archive_path)
    source_path.mkdir(parents=True)
    run('aunpack', '-X', build_path, archive_path)
    if not source_path.exists():
        # NOTE: if this happens oftern (it shouldn't), consider using
        #       atool's --save-outdir option above
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
    _copy_srcpkg_files(build_path, out_path)
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


def install_build_deps(
        srcpkg_path,
        **kwargs):
    interactive = kwargs.get('interactive', False)

    log.info("installing build deps using apt-get build-dep")
    cmd = ['apt-get', 'build-dep']
    env = {}
    if not interactive:
        cmd.append('-y')
        env['DEBIAN_FRONTEND'] = 'noninteractive'

    cmd.append(srcpkg_path.resolve())
    sudo(*cmd, env=env, direct=True)


def install_custom_packages(
        packages,
        **kwargs):

    def local_path(pkg):
        """
        apt install is able to install local packages
        as long as they use full path or relative including ./
        """
        p = str(pkg)
        if p[0] not in '/\\.':
            return "./%s" % p
        return p

    interactive = kwargs.get('interactive', False)

    cmd = ['apt', 'install']
    env = {}
    if not interactive:
        env['DEBIAN_FRONTEND'] = 'noninteractive'
        cmd += ['-y']

    cmd += list(map(local_path, packages))
    sudo(*cmd, env=env, direct=True)


def install_distro_packages(
        packages,
        **kwargs):
    interactive = kwargs.get('interactive', False)

    cmd = ['apt-get', 'install']
    env = {}
    if not interactive:
        env['DEBIAN_FRONTEND'] = 'noninteractive'
        cmd += ['-y']

    cmd += packages
    sudo(*cmd, env=env, direct=True)
