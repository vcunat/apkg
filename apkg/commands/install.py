"""
install packages using native distro package manager

Usage: apkg install (<package> | -f <file>)...
                    [-D] [-d <distro>] [-y]

Arguments:
  <package>...                    one or more packages to install
  -f <file>, --file-list <file>   file containing list of packages to install
                                  "-" for stdin (implies -y/--yes)

Options:
  -D, --distro-pkgs               install packages from distro repos
                                  default: install packages from package files
  -d <distro>, --distro <distro>  set target distro
                                  default: current distro
  -y, --yes                       non-interactive mode
                                  default: interactive (distro tool defualts)

Supply one or more <package> to install and/or use -f <file>
to read packages from specified <file>, one package per line.

Use "-f -" to read packages from standard input, i.e.

    apkg build | apkg install -f -

""" # noqa

from docopt import docopt

from apkg.lib import install


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    results = install.install_packages(
        packages=args['<package>'],
        file_list=args['--file-list'],
        distro_pkgs=args['--distro-pkgs'],
        distro=args['--distro'],
        interactive=not args['--yes'],
    )
    return results
