"""
apkg lib for handling package builds
"""
import shutil

from apkg import adistro
from pathlib import Path
from apkg import exception
from apkg.log import getLogger
from apkg.project import Project
from apkg.lib import srcpkg as _srcpkg


log = getLogger(__name__)


def build_package(
        srcpkg=None,
        archive=None,
        upstream=False,
        version=None,
        release=None,
        distro=None,
        install_dep=False,
        isolated=False,
        use_cache=True,
        project=None):
    log.bold('building package')

    proj = project or Project()
    distro = adistro.distro_arg(distro)
    use_cache = proj.cache.enabled(use_cache)
    log.info("target distro: %s" % distro)

    if srcpkg:
        # use existing source package
        srcpkg_path = Path(srcpkg)
        if not srcpkg_path.exists():
            raise exception.SourcePackageNotFound(
                srcpkg=srcpkg, type=distro)
        log.info("using existing source package: %s" % srcpkg_path)
    else:
        # make source package
        srcpkg_path = _srcpkg.make_srcpkg(
            archive=archive,
            version=version,
            release=release,
            distro=distro,
            upstream=upstream,
            project=proj,
            use_cache=use_cache)

    if use_cache and not upstream:
        cache_name = 'pkg/dev/%s' % distro
        pkgs = proj.cache.get(cache_name, proj.checksum)
        if pkgs:
            log.success(
                "reuse %d cached packages from: %s",
                len(pkgs), pkgs[0].parent)
            return pkgs

    if install_dep:
        # install build deps if requested
        install_build_deps(
            srcpkg=srcpkg_path,
            distro=distro)

    # fetch pkgstyle (deb, rpm, arch, ...)
    template = proj.get_template_for_distro(distro)
    pkgstyle = template.pkgstyle

    # get needed paths
    nvr = pkgstyle.get_srcpkg_nvr(srcpkg_path)
    build_path = proj.package_build_path / distro / nvr
    out_path = proj.package_out_path / distro / nvr
    log.info("source package NVR: %s", nvr)
    log.info("build dir: %s", build_path)
    log.info("result dir: %s", out_path)
    # ensure build build doesn't exist
    if build_path.exists():
        log.info("removing existing build dir: %s" % build_path)
        shutil.rmtree(build_path)
    # ensure output dir doesn't exist
    if out_path.exists():
        log.info("removing existing result dir: %s" % out_path)
        shutil.rmtree(out_path)

    # build package using chosen distro packaging style
    pkgs = pkgstyle.build_packages(
        build_path, out_path, srcpkg_path,
        isolated=isolated,
    )
    if not pkgs:
        msg = ("package build reported success but there are "
               "no packages:\n\n%s" % out_path)
        raise exception.UnexpectedCommandOutput(msg=msg)
    log.success("built %s packages in: %s", len(pkgs), out_path)

    if use_cache and not upstream:
        fns = list(map(str, pkgs))
        proj.cache.update(
            cache_name, proj.checksum, fns)

    return pkgs


def install_build_deps(
        srcpkg=None,
        archive=None,
        upstream=False,
        version=None,
        release=None,
        distro=None,
        interactive=False):
    log.bold('installing build deps')

    proj = Project()
    distro = adistro.distro_arg(distro)
    log.info("target distro: %s" % distro)

    if srcpkg:
        # use existing source package
        srcpkg_path = Path(srcpkg)
        if not srcpkg_path.exists():
            raise exception.SourcePackageNotFound(
                srcpkg=srcpkg, type=distro)
        log.info("using existing source package: %s" % srcpkg_path)
    else:
        # make source package
        srcpkg_path = _srcpkg.make_srcpkg(
            archive=archive,
            version=version,
            release=release,
            distro=distro,
            upstream=upstream)

    # fetch pkgstyle (deb, rpm, arch, ...)
    template = proj.get_template_for_distro(distro)
    pkgstyle = template.pkgstyle

    pkgstyle.install_build_deps(
        srcpkg_path,
        interactive=interactive)
