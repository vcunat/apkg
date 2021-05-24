from apkg import adistro
from apkg import ex
from apkg.log import getLogger
from apkg import pkgstyle


log = getLogger(__name__)


def system_setup(
        isolated=False,
        distro=None,
        interactive=False):
    log.bold("system setup for packaging")

    distro = adistro.distro_arg(distro)
    log.info("target distro: %s", distro)

    style = pkgstyle.get_pkgstyle_for_distro(distro)
    if not style:
        raise ex.DistroNotSupported(distro=distro)
    log.info("target pkgstyle: %s", style.name)

    distro_reqs = getattr(style, 'DISTRO_REQUIRES', {})
    reqs = distro_reqs.get('core', [])
    if isolated:
        reqs += distro_reqs.get('isolated', [])
    if reqs:
        pkgstyle.call_pkgstyle_fun(
            style, 'install_distro_packages',
            reqs,
            interactive=interactive)
    else:
        log.info("no distro packages required")

    log.success("system ready for packaging")
