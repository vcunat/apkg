"""
create source package (files to build package from)

usage: apkg make-source-package [-u] [-a <ar>] [-v <ver>] [-r <rls>]

options:
  -u, --upstream             use upstream archive / apkg get-source
                             default: use dev archvie / apkg make-source
  -a <ar>, --archive <ar>    use specified archive (path or name)
  -v <ver>, --version <ver>  set package version
  -r <rls>, --release <rls>  set package release
"""

from docopt import docopt

from apkg import exception
from apkg import log
from apkg.project import Project
from apkg.lib import ar


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    return make_source_package(
            upstream=args['--upstream'],
            archive=args['--archive'],
            version=args['--version'],
            release=args['--release'])


def make_source_package(archive=None, version=None, release=None, upstream=False):
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

    log.info("source package version: %s-%s", version, release)

    raise exception.NotImplemented(
            msg="TODO: build package from archive: %s" % ar_path)
