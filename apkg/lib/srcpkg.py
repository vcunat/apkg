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


def make_source_package(
        archive=None, version=None, release=None,
        distro=None, upstream=False):
    log.verbose('creating source package')

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
    template = proj.get_package_template_for_distro(distro)
    if not template:
        tdir = proj.package_templates_path
        msg = ("missing package template for distro: %s\n\n"
               "you can add it into: %s" % (distro, tdir))
        raise exception.MissingPackagingTemplate(msg=msg)
    ps = template.package_style
    log.info("package style: %s", ps.name)
    log.info("package template: %s", template.path)
    log.info("package archive: %s", ar_path)

    # get needed paths
    pkg_name = ps.get_package_name(template.path)
    nvr = "%s-%s-%s" % (pkg_name, version, release)
    build_path = proj.source_package_build_path / distro / nvr
    out_path = proj.source_package_out_path / distro / nvr
    log.info("package name: %s", nvr)
    log.info("build dir: %s", build_path)
    log.info("result dir: %s", out_path)

    # prepare new build dir
    if build_path.exists():
        log.info("removing existing build dir: %s" % build_path)
        shutil.rmtree(build_path)
    os.makedirs(py35path(build_path), exist_ok=True)
    # ensure output dir doesn't exist
    if out_path.exists():
        log.info("removing existing result dir: %s" % out_path)
        shutil.rmtree(out_path)

    # prepare vars accessible from templates
    vars = {
        'name': pkg_name,
        'version': version,
        'release': release,
        'nvr': nvr,
        'distro': distro,
    }
    # create source package using desired package style
    template.package_style.build_source_package(
        build_path,
        out_path,
        archive_path=ar_path,
        package_template=template,
        vars=vars)

    if out_path.exists():
        log.success("made source package: %s", out_path)
    else:
        msg = ("source package build reported success but there are "
               "no results:\n\n%s" % out_path)
        raise exception.UnexpectedCommandOutput(msg=msg)
    return out_path
