"""
apkg lib for handling source archives
"""
import os
from pathlib import Path
import shutil

from apkg import adistro
from apkg import exception
from apkg import log
from apkg import pkgstyle
from apkg.project import Project
from apkg.lib import ar
from apkg.util.cmd import run


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
        distro = adistro.id()
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
    log.info("package template path: %s", template.path)
    # get needed paths
    pkg_name = ps.get_package_name(template.path)
    nvr = "%s-%s-%s" % (pkg_name, version, release)
    build_path = proj.source_package_build_path / distro / nvr
    out_path = proj.source_package_out_path / distro / nvr
    log.info("source package: %s", nvr)
    log.info("build dir: %s", build_path)
    log.info("output dir: %s", out_path)

    # prepare vars accessible from templates
    vars = {
        'version': version,
        'release': release,
        'distro': distro,
        'nvr': nvr,
    }
    # render package template
    template.render(build_path, vars=vars)

    # create source package using desired package style
    log.info("building source package using style: %s",
             template.package_style.name)
    template.package_style.build_source_package(
        build_path,
        archive_path=ar_path,
        vars=vars)

    # prepare output dir and copy result
    if out_path.exists():
        log.info("removing existing output dir: %s" % out_path)
        shutil.rmtree(out_path)
    log.info("copying source package to: %s" % out_path)
    os.makedirs(out_path.parent, exist_ok=True)
    shutil.copytree(build_path, out_path)
    log.success("made source package: %s", out_path)
    return out_path
