"""
install build dependencies

Usage: apkg build-dep ([-u] | [-s <srcpkg>] | [-a <ar>] )
                       [-v <ver>] [-r <rls>] [-d <distro>]
                       [-y]

Options:
  -s <srcpkg>, --srcpkg <srcpkg>  use specified source package (path or name)
  -a <ar>, --archive <ar>         use specified archive (path or name)
  -u, --upstream                  use upstream archive / apkg get-source
                                  default: use dev archvie / apkg make-source
  -v <ver>, --version <ver>       set package version
  -r <rls>, --release <rls>       set package release
  -d <distro>, --distro <distro>  set target distro
                                  default: current distro
  -y, --yes                       non-interactive mode
                                  default: interactive (distro tool defualts)
""" # noqa

from docopt import docopt

from apkg.lib import build


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    return build.install_build_deps(
            srcpkg=args['--srcpkg'],
            archive=args['--archive'],
            upstream=args['--upstream'],
            version=args['--version'],
            release=args['--release'],
            distro=args['--distro'],
            interactive=not args['--yes'],
            )
