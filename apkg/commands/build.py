from pathlib import Path

import click

from apkg import adistro
from apkg.cache import file_checksum
from apkg import ex
from apkg.commands.build_dep import build_dep
from apkg.commands.srcpkg import srcpkg as make_srcpkg
from apkg.log import getLogger
from apkg.project import Project
from apkg.util import common
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


@click.command(name="build")
@click.argument('input_files', nargs=-1)
@click.option('-s', '--srcpkg', is_flag=True,
              help="use source package")
@click.option('-a', '--archive', is_flag=True,
              help="use template (/build srcpkg) from archive")
@click.option('-u', '--upstream', is_flag=True,
              help="use upstream template / archive / srcpkg")
@click.option('-v', '--version',
              help=("upstream archive version to use"
                    ", implies --upstream"
                    ", exclusive with --srcpkg and --archive"))
@click.option('-r', '--release',
              help="set packagge release  [default: 1]")
@click.option('-d', '--distro',
              help="override target distro  [default: current]")
@click.option('-O', '--result-dir',
              help=("put results into specified dir"
                    "  [default: pkg/srcpkg/DISTRO/NVR]"))
@click.option('--cache/--no-cache', default=True, show_default=True,
              help="enable/disable cache")
@click.option('-F', '--file-list', 'input_file_lists', multiple=True,
              help=("specify text file listing one input file per line"
                    ", use '-' to read from stdin"))
@click.option('-i', '--install-dep', is_flag=True,
              help="install build dependencies on host (build-dep)")
@click.option('-I', '--isolated', is_flag=True,
              help="use isolated builder (pbuilder, mock, ...)")
@click.help_option('-h', '--help',
                   help="show this help message")
def cli_build(*args, **kwargs):
    """
    build packages
    """
    results = build(*args, **kwargs)
    common.print_results(results)
    return results


def build(
        srcpkg=False,
        archive=False,
        upstream=False,
        input_files=None,
        input_file_lists=None,
        version=None,
        release=None,
        distro=None,
        result_dir=None,
        install_dep=False,
        isolated=False,
        cache=True,
        project=None):
    """
    build packages
    """
    log.bold('building packages')

    proj = project or Project()
    distro = adistro.distro_arg(distro)
    log.info("target distro: %s", distro)
    use_cache = proj.cache.enabled(cache)

    if srcpkg:
        if version:
            raise ex.InvalidInput(
                fail="--srcpkg and --version options are mutually exclusive")
        # use existing source package
        infiles = common.parse_input_files(input_files, input_file_lists)
    else:
        # make source package
        infiles = make_srcpkg(
            archive=archive,
            input_files=input_files,
            input_file_lists=input_file_lists,
            upstream=upstream,
            version=version,
            release=release,
            distro=distro,
            project=proj,
            cache=use_cache)

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
                build_dep(
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


APKG_CLI_COMMANDS = [cli_build]
