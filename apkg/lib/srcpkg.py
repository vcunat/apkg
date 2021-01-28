"""
apkg lib for handling source archives
"""
import os
import shutil

from apkg import adistro
from apkg.compat import py35path
from apkg import exception
from apkg.log import getLogger
from apkg.project import Project
from apkg.lib import ar


log = getLogger(__name__)


def make_srcpkg(
        archive=None, version=None, release=None,
        distro=None, upstream=False, use_cache=True,
        project=None):
    log.bold('creating source package')

    proj = project or Project()
    distro = adistro.distro_arg(distro)
    use_cache = proj.cache.enabled(use_cache)
    log.info("target distro: %s" % distro)

    if not release:
        release = '1'

    if archive:
        # archive specified - find it
        ar_path = ar.find_archive(archive, upstream=upstream, project=proj)
        version = ar.get_archive_version(ar_path, version=version)
    else:
        # archive not specified - use make_archive or get_archive
        if upstream:
            ar_path = ar.get_archive(
                version=version,
                project=proj,
                use_cache=use_cache)
        else:
            ar_path = ar.make_archive(
                version=version,
                project=proj,
                use_cache=use_cache)
        version = ar.get_archive_version(ar_path, version=version)

    # --upstream builds aren't well supported yet - don't cache for now
    if use_cache and not upstream:
        cache_name = 'srcpkg/dev/%s' % distro
        srcpkg_path = proj.cache.get(cache_name, proj.checksum)
        if srcpkg_path:
            log.success("reuse cached source package: %s", srcpkg_path)
            return srcpkg_path

    # fetch correct package template
    template = proj.get_template_for_distro(distro)
    if not template:
        tdir = proj.templates_path
        msg = ("missing package template for distro: %s\n\n"
               "you can add it into: %s" % (distro, tdir))
        raise exception.MissingPackagingTemplate(msg=msg)
    ps = template.pkgstyle
    log.info("package style: %s", ps.name)
    log.info("package template: %s", template.path)
    log.info("package archive: %s", ar_path)

    # get needed paths
    pkg_name = ps.get_template_name(template.path)
    nvr = "%s-%s-%s" % (pkg_name, version, release)
    build_path = proj.srcpkg_build_path / distro / nvr
    out_path = proj.srcpkg_out_path / distro / nvr
    log.info("package NVR: %s", nvr)
    log.info("build dir: %s", build_path)
    log.info("result dir: %s", out_path)

    # prepare new build dir
    if build_path.exists():
        log.info("removing existing build dir: %s" % build_path)
        shutil.rmtree(py35path(build_path))
    os.makedirs(py35path(build_path), exist_ok=True)
    # ensure output dir doesn't exist
    if out_path.exists():
        log.info("removing existing result dir: %s" % out_path)
        shutil.rmtree(out_path)

    # prepare vars accessible from templates
    env = {
        'name': pkg_name,
        'version': version,
        'release': release,
        'nvr': nvr,
        'distro': distro,
    }
    # create source package using desired package style
    srcpkg_path = template.pkgstyle.build_srcpkg(
        build_path,
        out_path,
        archive_path=ar_path,
        template=template,
        env=env)

    if srcpkg_path.exists():
        log.success("made source package: %s", srcpkg_path)
    else:
        msg = ("source package build reported success but there are "
               "no results:\n\n%s" % srcpkg_path)
        raise exception.UnexpectedCommandOutput(msg=msg)

    if use_cache and not upstream:
        proj.cache.update(
            cache_name, proj.checksum, str(srcpkg_path))

    return srcpkg_path
