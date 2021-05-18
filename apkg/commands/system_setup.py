"""
setup system for packaging

Install native distro packages required for packaging.

Usage: apkg system-setup [-I] [-d <distro>] [-y]

Options:
  -I, --isolated          also install packages for isolated build
                          default: install core packages only
  -d, --distro <distro>   override target distro
                          default: current distro
  -y, --yes               non-interactive mode
                          default: interactive (distro tool defualts)
""" # noqa

from docopt import docopt

from apkg.lib import system


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    return system.system_setup(
        isolated=args['--isolated'],
        distro=args['--distro'],
        interactive=not args['--yes'],
        )
