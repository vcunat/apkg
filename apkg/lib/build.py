"""
apkg lib for handling package builds
"""
from pathlib import Path
import shutil

from apkg import adistro
from apkg.cache import file_checksum
from apkg import exception
from apkg.lib import srcpkg as _srcpkg
from apkg.lib import common
from apkg.log import getLogger
from apkg.project import Project


log = getLogger(__name__)


def build_package(
        upstream=False,
        srcpkg=None,
        archive=None,
        version=None,
        release=None,
        distro=None,
        result_dir=None,
        install_dep=False,
        isolated=False,
        use_cache=True,
        project=None):
    log.bold('building package')

    proj = project or Project()
    distro = adistro.distro_arg(distro)
    log.info("target distro: %s", distro)

    if srcpkg:
        # use existing source package
        srcpkg_path = Path(srcpkg)
        if not srcpkg_path.exists():
            raise exception.SourcePackageNotFound(
                srcpkg=srcpkg, type=distro)
        log.info("using existing source package: %s", srcpkg_path)
    else:
        # make source package
        srcpkg_path = Path(_srcpkg.make_srcpkg(
            archive=archive,
            version=version,
            release=release,
            distro=distro,
            upstream=upstream,
            project=proj,
            use_cache=use_cache)[0])

    use_cache = proj.cache.enabled(use_cache)
    if use_cache:
        cache_name = 'pkg/%s' % distro
        cache_key = file_checksum(srcpkg_path)
        cached = common.get_cached_paths(
            proj, cache_name, cache_key, result_dir)
        if cached:
            log.success("reuse %d cached packages", len(cached))
            return cached

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
    if result_dir:
        result_path = Path(result_dir)
    else:
        result_path = proj.package_out_path / distro / nvr
    log.info("source package NVR: %s", nvr)
    log.info("build dir: %s", build_path)
    log.info("result dir: %s", result_path)
    # ensure build build doesn't exist
    if build_path.exists():
        log.info("removing existing build dir: %s", build_path)
        shutil.rmtree(build_path)
    # ensure result dir doesn't exist unless specified
    if not result_dir and result_path.exists():
        log.info("removing existing result dir: %s", result_path)
        shutil.rmtree(result_path)

    # build package using chosen distro packaging style
    pkgs = pkgstyle.build_packages(
        build_path, result_path, srcpkg_path,
        isolated=isolated,
    )
    if not pkgs:
        msg = ("package build reported success but there are "
               "no packages:\n\n%s" % result_path)
        raise exception.UnexpectedCommandOutput(msg=msg)
    log.success("built %s packages in: %s", len(pkgs), result_path)

    if use_cache and not upstream:
        fns = list(map(str, pkgs))
        proj.cache.update(
            cache_name, cache_key, fns)

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
    log.info("target distro: %s", distro)

    if srcpkg:
        # use existing source package
        srcpkg_path = Path(srcpkg)
        if not srcpkg_path.exists():
            raise exception.SourcePackageNotFound(
                srcpkg=srcpkg, type=distro)
        log.info("using existing source package: %s", srcpkg_path)
    else:
        # make source package
        srcpkg_path = _srcpkg.make_srcpkg(
            archive=archive,
            version=version,
            release=release,
            distro=distro,
            upstream=upstream)[0]

    # fetch pkgstyle (deb, rpm, arch, ...)
    template = proj.get_template_for_distro(distro)
    pkgstyle = template.pkgstyle

    pkgstyle.install_build_deps(
        srcpkg_path,
        distro=distro,
        interactive=interactive)
