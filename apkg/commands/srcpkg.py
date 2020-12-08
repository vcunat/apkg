"""
create source package (files to build package from)

usage: apkg srcpkg [-u] [-a <ar>] [-v <ver>] [-r <rls>] [-d <distro>]

options:
  -u, --upstream                  use upstream archive / apkg get-source
                                  default: use dev archvie / apkg make-source
  -a <ar>, --archive <ar>         use specified archive (path or name)
  -v <ver>, --version <ver>       set package version
  -r <rls>, --release <rls>       set package release
  -d <distro>, --distro <distro>  set target distro
                                  default: current distro
""" # noqa

from docopt import docopt

from apkg.lib import srcpkg


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    out_srcpkg = srcpkg.make_source_package(
            upstream=args['--upstream'],
            archive=args['--archive'],
            version=args['--version'],
            release=args['--release'],
            distro=args['--distro'])
    print(out_srcpkg)
    return out_srcpkg
