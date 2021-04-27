"""
install or list build dependencies

Usage: apkg build-dep [-l] [-u] [-s] [-a] [<file> | -F <file-list>]...
                      [-d <distro>] [-y]

Arguments:
  <file>                  specify input <file>s (when using -s or -a)
  -F, --file-list <fl>    specify text file listing one input file per line
                          use '-' to read from stdin

Options:
  -l, --list              list buid deps only, don't install
                          default: install deps
  -u, --upstream          use upstream template / archive / srcpkg
                          default: use dev template / archive / srcpkg
  -s, --srcpkg            use source package
                          default: use template
  -a, --archive           use template (/build srcpkg) from archive
                          default: use dev template
  -d, --distro <distro>   override target distro
                          default: current distro
  -y, --yes               non-interactive mode
                          default: interactive (distro tool defualts)
""" # noqa

from docopt import docopt

from apkg.lib import deps


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    return deps.build_dep(
        list_only=args['--list'],
        upstream=args['--upstream'],
        srcpkg=args['--srcpkg'],
        archive=args['--archive'],
        input_files=args['<file>'],
        input_file_lists=args['--file-list'],
        distro=args['--distro'],
        interactive=not args['--yes'],
        )
