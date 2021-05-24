import sys

import click

from apkg import adistro
from apkg import ex
from apkg.log import getLogger
from apkg import pkgstyle


log = getLogger(__name__)


@click.command(name="install")
@click.argument('packages', nargs=-1)
@click.option('-D', '--distro-pkgs', is_flag=True,
              help="install packages from distro repos")
@click.option('-d', '--distro',
              help="override target distro  [default: current]")
@click.option('--ask/--no-ask', 'interactive',
              default=False, show_default=True,
              help="enable/disable interactive mode")
# TODO: once py3.5 is dropped, add hidden=True
@click.option('-y', '--yes', 'interactive', flag_value=False,
              help="compat alias for --no-ask")
@click.option('-F', '--file-list', 'input_file_lists', multiple=True,
              help=("specify text file listing one input package per line"
                    ", use '-' to read from stdin"))
@click.help_option('-h', '--help',
                   help="show this help message")
def cli_install(*args, **kwargs):
    """
    install packages using native package manager

    Supply one or more package to install and/or use -F <file-list>
    to read packages from specified file, one package per line.
    """
    return install(*args, **kwargs)


def install(
        packages=None,
        input_file_lists=None,
        distro_pkgs=False,
        distro=None,
        interactive=False):
    """
    install packages using native package manager
    """
    log.bold("installing packages")

    distro = adistro.distro_arg(distro)
    log.info("target distro: %s", distro)
    pkgs = packages
    for fn in input_file_lists:
        if fn == '-':
            f = sys.stdin
            # unable to get interactive input when piping stdin
            interactive = False
        else:
            f = open(fn)
        pkgs = pkgs + list(map(str.strip, f.readlines()))

    ps = pkgstyle.get_pkgstyle_for_distro(distro)
    if not ps:
        raise ex.DistroNotSupported(distro=distro)
    log.info("target pkgstyle: %s", ps.name)

    if distro_pkgs:
        result = ps.install_distro_packages(
            pkgs, distro=distro, interactive=interactive)
    else:
        result = ps.install_custom_packages(
            pkgs, distro=distro, interactive=interactive)

    log.success("installed %s packages", len(pkgs))

    return result


APKG_CLI_COMMANDS = [cli_install]
