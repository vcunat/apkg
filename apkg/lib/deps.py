"""
apkg lib for handling (build) dependencies
"""
from apkg import adistro
from apkg.pkgstyle import call_pkgstyle_fun
from apkg.lib import ar
from apkg.lib import common
from apkg.lib import srcpkg as _srcpkg
from apkg.log import getLogger
from apkg.project import Project
from apkg.util.archive import unpack_archive


log = getLogger(__name__)


def build_dep(
        upstream=False,
        srcpkg=False,
        archive=False,
        input_files=None,
        input_file_lists=None,
        list_only=False,
        distro=None,
        interactive=False,
        project=None):
    action = 'listing' if list_only else 'installing'
    log.bold('%s build deps', action)

    proj = project or Project()
    distro = adistro.distro_arg(distro)
    log.info("target distro: %s", distro)

    # fetch pkgstyle (deb, rpm, arch, ...)
    template = proj.get_template_for_distro(distro)
    pkgstyle = template.pkgstyle

    infiles = common.parse_input_files(input_files, input_file_lists)

    if srcpkg:
        # use source package to determine deps
        if archive or not infiles:
            # build source package
            srcpkg_files = _srcpkg.make_srcpkg(
                archive=archive,
                distro=distro,
                input_files=input_files,
                input_file_lists=input_file_lists,
                upstream=upstream,
                project=proj)
        else:
            # use specified source package
            srcpkg_files = infiles

        common.ensure_input_files(srcpkg_files)
        srcpkg_path = srcpkg_files[0]

        log.info("build deps from srcpkg: %s", srcpkg_path)
        deps = call_pkgstyle_fun(
            pkgstyle, 'get_build_deps_from_srcpkg',
            srcpkg_path)
    else:
        # use tempalte to determine deps
        if archive:
            archive_files = infiles

        if upstream:
            archive = True
            archive_files = ar.get_archive(project=proj)

        if archive:
            common.ensure_input_files(archive_files)
            archive_path = archive_files[0]
            log.info("unpacking archive: %s", archive_path)
            unpack_path = unpack_archive(
                archive_path, proj.unpacked_archive_path)
            log.info("loading template from archive: %s", unpack_path)
            # load project with input_path from archive
            aproj = Project(path=unpack_path)
            template = aproj.get_template_for_distro(distro)

        log.info("build deps from template: %s", template.path)
        deps = call_pkgstyle_fun(
            pkgstyle, 'get_build_deps_from_template',
            template.path, distro=distro)

    if list_only:
        for dep in deps:
            print(dep)
        return deps

    log.info("installing %s build deps...", len(deps))
    return call_pkgstyle_fun(
        pkgstyle, 'install_build_deps',
        deps,
        distro=distro,
        interactive=interactive)
