from pathlib import Path

import click

from apkg import adistro
from apkg.cache import file_checksum
from apkg import ex
from apkg.util import common
from apkg.commands.get_archive import get_archive
from apkg.commands.make_archive import make_archive
from apkg.log import getLogger
from apkg.project import Project
from apkg.util.archive import unpack_archive, get_archive_version
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


@click.command(name="srcpkg")
@click.argument('input_files', nargs=-1)
@click.option('-a', '--archive', is_flag=True,
              help="source package from speficied archive file(s)")
@click.option('-u', '--upstream', is_flag=True,
              help="upstream source package from archive templates")
@click.option('-v', '--version',
              help=("upstream archive version to use"
                    ", implies --upstream, exclusive with --archive"))
@click.option('-r', '--release',
              help="set packagge release  [default: 1]")
@click.option('-d', '--distro',
              help="set target distro  [default: current]")
@click.option('-O', '--result-dir',
              help=("put results into specified dir"
                    "  [default: pkg/srcpkg/DISTRO/NVR]"))
@click.option('--render-template', is_flag=True,
              help="only render source package template")
@click.option('--cache/--no-cache', default=True, show_default=True,
              help="enable/disable cache")
@click.option('-F', '--file-list', 'input_file_lists', multiple=True,
              help=("specify text file listing one input file per line"
                    ", use '-' to read from stdin"))
@click.help_option('-h', '--help',
                   help="show this help message")
def cli_srcpkg(*args, **kwargs):
    """
    create source package (files to build packages from)
    """
    results = srcpkg(*args, **kwargs)
    common.print_results(results)
    return results


def srcpkg(
        archive=False,
        input_files=None,
        input_file_lists=None,
        upstream=False,
        version=None,
        release=None,
        distro=None,
        result_dir=None,
        render_template=False,
        cache=True,
        project=None):
    """
    create source package
    """
    srcpkg_type = 'upstream' if upstream else 'dev'
    if render_template:
        log.bold('rendering %s source package template', srcpkg_type)
    else:
        log.bold('creating %s source package', srcpkg_type)

    if version:
        # --version implies --upstream
        upstream = True
        if archive:
            raise ex.InvalidInput(
                fail="--archive and --version options are mutually exclusive")

    proj = project or Project()
    distro = adistro.distro_arg(distro)
    log.info("target distro: %s", distro)
    use_cache = proj.cache.enabled(cache)

    if not release:
        release = '1'

    infiles = common.parse_input_files(input_files, input_file_lists)

    if not archive:
        # archive not specified - use make_archive or get_archive
        if infiles:
            instr = ", ".join([str(i) for i in infiles])
            raise ex.InvalidInput(
                fail="unexpected input file(s): %s" % instr)

        if upstream:
            infiles = get_archive(
                version=version,
                cache=use_cache,
                project=proj)
        else:
            infiles = make_archive(
                cache=use_cache,
                project=proj)

    common.ensure_input_files(infiles)
    ar_path = infiles[0]
    version = get_archive_version(ar_path)

    use_cache = proj.cache.enabled(use_cache) and not render_template
    if use_cache:
        cache_name = 'srcpkg/%s/%s' % (srcpkg_type, distro)
        if upstream:
            cache_key = file_checksum(ar_path)
        else:
            cache_key = proj.checksum
        cached = common.get_cached_paths(
            proj, cache_name, cache_key, result_dir)
        if cached:
            log.success("reuse cached source package: %s", cached[0])
            return cached

    if upstream:
        # --upstream mode - use distro/ from archive
        log.info("unpacking upstream archive: %s", ar_path)
        unpack_path = unpack_archive(ar_path, proj.unpacked_archive_path)
        input_path = unpack_path / 'distro'
        log.info("loading upstream project input: %s", input_path)
        # reload project with input_path from archive
        proj.load(input_path=input_path, output_path=proj.output_path)

    # fetch correct package template
    template = proj.get_template_for_distro(distro)
    if not template:
        tdir = proj.templates_path
        msg = ("missing package template for distro: %s\n\n"
               "you can add it into: %s" % (distro, tdir))
        raise ex.MissingPackagingTemplate(msg=msg)
    ps = template.pkgstyle
    log.info("package style: %s", ps.name)
    log.info("package template: %s", template.path)
    log.info("package archive: %s", ar_path)

    # get needed paths
    pkg_name = ps.get_template_name(template.path)
    nvr = "%s-%s-%s" % (pkg_name, version, release)
    build_path = proj.srcpkg_build_path / distro / nvr
    if result_dir:
        out_path = Path(result_dir)
    else:
        out_path = proj.srcpkg_out_path / distro / nvr
    log.info("package NVR: %s", nvr)
    log.info("build dir: %s", build_path)
    log.info("result dir: %s", out_path)

    # prepare new build dir
    if build_path.exists():
        log.info("removing existing build dir: %s", build_path)
        shutil.rmtree(build_path)
    build_path.mkdir(parents=True, exist_ok=True)
    # ensure output dir doesn't exist unless it was specified
    if not result_dir and out_path.exists():
        log.info("removing existing result dir: %s", out_path)
        shutil.rmtree(out_path)

    # prepare vars accessible from templates
    env = {
        'name': pkg_name,
        'version': version,
        'release': release,
        'nvr': nvr,
        'distro': distro,
    }
    if render_template:
        # render template only, don't build srcpkg
        if result_dir:
            # respect --result-dir when rendering template
            build_path = out_path
        template.render(build_path, env)
        log.success("rendered source package template: %s", build_path)
        return [build_path]

    # create source package using desired package style
    results = template.pkgstyle.build_srcpkg(
        build_path,
        out_path,
        archive_paths=infiles,
        template=template,
        env=env)

    # check reported results exist
    for p in results:
        if not Path(p).exists():
            msg = ("source package build reported success but result is "
                   "missing:\n\n%s" % p)
            raise ex.UnexpectedCommandOutput(msg=msg)

    # first line of output is a source package by convention
    srcpkg_path, *rest = results
    # sort additional srcpkg files for determinism
    results = [srcpkg_path] + sorted(rest)

    log.success("made source package: %s", srcpkg_path)

    if use_cache:
        proj.cache.update(
            cache_name, cache_key, results)

    return results


APKG_CLI_COMMANDS = [cli_srcpkg]
