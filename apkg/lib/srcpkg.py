"""
apkg lib for handling source archives
"""
from pathlib import Path

from apkg import adistro
from apkg.cache import file_checksum
from apkg import ex
from apkg.lib import ar
from apkg.lib import common
from apkg.log import getLogger
from apkg.project import Project
from apkg.util.archive import unpack_archive
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


def make_srcpkg(
        upstream=False,
        archive=False,
        input_files=None,
        input_file_lists=None,
        version=None,
        release=None,
        distro=None,
        result_dir=None,
        use_cache=True,
        render_template=False,
        project=None):
    srcpkg_type = 'upstream' if upstream else 'dev'
    if render_template:
        log.bold('rendering %s source package template', srcpkg_type)
    else:
        log.bold('creating %s source package', srcpkg_type)

    proj = project or Project()
    distro = adistro.distro_arg(distro)
    log.info("target distro: %s", distro)

    if not release:
        release = '1'

    if archive:
        # use existing archive
        infiles = common.parse_input_files(input_files, input_file_lists)
    else:
        # archive not specified - use make_archive or get_archive
        if upstream:
            infiles = ar.get_archive(
                version=version,
                project=proj,
                use_cache=use_cache)
        else:
            infiles = ar.make_archive(
                version=version,
                project=proj,
                use_cache=use_cache)

    common.ensure_input_files(infiles)
    ar_path = infiles[0]
    version = ar.get_archive_version(ar_path, version=version)

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
    log.success("made source package: %s", results[0])

    if use_cache:
        proj.cache.update(
            cache_name, cache_key, results)

    return results
