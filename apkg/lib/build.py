"""
apkg lib for handling package builds
"""
from pathlib import Path

from apkg import adistro
from apkg.cache import file_checksum
from apkg import ex
from apkg.lib import srcpkg as _srcpkg
from apkg.lib import common, deps
from apkg.log import getLogger
from apkg.project import Project
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


def build_package(
        upstream=False,
        srcpkg=False,
        archive=False,
        input_files=None,
        input_file_lists=None,
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
        infiles = common.parse_input_files(input_files, input_file_lists)
    else:
        # make source package
        infiles = _srcpkg.make_srcpkg(
            archive=archive,
            input_files=input_files,
            input_file_lists=input_file_lists,
            version=version,
            release=release,
            distro=distro,
            upstream=upstream,
            project=proj,
            use_cache=use_cache)

    common.ensure_input_files(infiles)
    srcpkg_path = infiles[0]
    if srcpkg:
        log.info("using existing source package: %s", srcpkg_path)

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
        if isolated:
            # doesn't make sense outside of host build
            log.warning("ignoring request to install deps in isolated build")
        else:
            # install build deps if requested
            try:
                deps.build_dep(
                    srcpkg=True,
                    input_files=[srcpkg_path],
                    distro=distro,
                    project=proj)
            except ex.DistroNotSupported as e:
                log.warning("%s - SKIPPING", e)

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
        build_path,
        result_path,
        srcpkg_paths=infiles,
        isolated=isolated)

    if not pkgs:
        msg = ("package build reported success but there are "
               "no packages:\n\n%s" % result_path)
        raise ex.UnexpectedCommandOutput(msg=msg)
    log.success("built %s packages in: %s", len(pkgs), result_path)

    if use_cache and not upstream:
        fns = list(map(str, pkgs))
        proj.cache.update(
            cache_name, cache_key, fns)

    return pkgs
