"""
Show status of current project

Usage: apkg status
"""

from docopt import docopt
import distro
import os

from apkg import log
from apkg.project import Project
from apkg import pkgstyle


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    print_status()


def print_status():
    proj = Project()

    msg = "project base path:        {t.bold}{path}{t.normal}"
    print(msg.format(path=proj.path.resolve(), t=log.T))

    msg = "project config:           {t.bold}{path}{t.normal}"
    if proj.config_path.exists():
        msg += " ({t.green}exists{t.normal})"
    else:
        msg += " ({t.warn}doesn't exist{t.normal})"
    print(msg.format(path=proj.config_path, t=log.T))

    msg = "packaging templates path: {t.bold}{path}{t.normal}"
    if proj.package_templates_path.exists():
        msg += " ({t.green}exists{t.normal})"
    else:
        msg += " ({t.red}doesn't exist{t.normal})"
    print(msg.format(path=proj.package_templates_path, t=log.T))

    print("packaging templates:")
    if proj.package_templates:
        msg_lines = []
        for path, style in proj.package_templates:
            short_path = os.path.join(*list(path.parts)[-3:])
            msg_lines.append("    {t.bold}%s{t.normal}: {t.green}%s{t.normal}"
                    % (short_path, style))
        msg = "\n".join(msg_lines)
    else:
        msg = "    {t.red}no packaging templates found{t.normal}"
    print(msg.format(dir=proj.package_templates_path, t=log.T))

    print()
    # distro status
    msg = "current distro: {t.cyan}{full}{t.normal} ({t.cyan}{id}{t.normal})"
    distro_full = " ".join(distro.linux_distribution()).rstrip()
    distro_id = distro.id()
    print(msg.format(full=distro_full, id=distro_id, t=log.T))

    msg = "    packaging style: "
    style, _ = pkgstyle.get_packaging_style_for_distro(distro_id)
    if style:
        msg += "{t.green}%s{t.normal}" % style
    else:
        msg += "{t.warn}unsupported{t.normal}"
    print(msg.format(t=log.T))
