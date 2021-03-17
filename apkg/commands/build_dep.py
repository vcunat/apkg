"""
install build dependencies

Usage: apkg build-dep [-u] [-s | -a] [<file> | -F <file-list>]...
                      [-d <distro>] [-y]

Arguments:
  <file>                  specify input <file>s (when using -s or -a)
  -F, --file-list <fl>    specify text file listing one input file per line
                          use '-' to read from stdin

Options:
  -u, --upstream          use upstream archive / apkg get-archive
                          default: dev archive / apkg make-archive
  -s, --srcpkg            use source package <file>s
  -a, --archive           use archive <files>s
                          default: use dev archvie / apkg make-source
  -d, --distro <distro>   set target distro
                          default: current distro
  -y, --yes               non-interactive mode
                          default: interactive (distro tool defualts)
""" # noqa

from docopt import docopt

from apkg.lib import build


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    # XXX: this will be refactored in following patch
    # disabling for now
    raise NotImplementedError
    return build.install_build_deps(
        srcpkg=args['--srcpkg'],
        archive=args['--archive'],
        upstream=args['--upstream'],
        version=args['--version'],
        release=args['--release'],
        distro=args['--distro'],
        interactive=not args['--yes'],
        )
