"""
apkg lib for handling source archives
"""
import os
import shutil

from apkg import adistro
from apkg.compat import py35path
from apkg import exception
from apkg import log
from apkg.project import Project
from apkg.lib import ar


def make_srcpkg(
        archive=None, version=None, release=None,
        distro=None, upstream=False):
    log.bold('creating source package')

    proj = Project()
    if not release:
        release = '1'

    if archive:
        # archive specified - find it
        ar_path = ar.find_archive(archive, upstream=upstream, project=proj)
        version = ar.get_archive_version(ar_path, version=version)
    else:
        # archive not specified - use make_archive or get_archive
        if upstream:
            ar_path = ar.get_archive(version=version, project=proj)
        else:
            ar_path = ar.make_archive(version=version, project=proj)
        version = ar.get_archive_version(ar_path, version=version)

    if distro:
        # convert custom distro string to idver format
        distro = adistro.distro2idver(distro)
    else:
        # use current distro by default
        distro = adistro.idver()
    log.info("target distro: %s" % distro)

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
    return srcpkg_path
