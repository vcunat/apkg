"""
apkg lib for handling package installation using native package manager
"""
import sys

from apkg import adistro
from apkg import ex
from apkg.log import getLogger
from apkg import pkgstyle


log = getLogger(__name__)


def install_packages(
        packages=None,
        file_list=None,
        distro_pkgs=False,
        distro=None,
        interactive=False):
    log.bold("installing packages")

    distro = adistro.distro_arg(distro)
    log.info("target distro: %s", distro)
    pkgs = packages
    for fn in file_list:
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
