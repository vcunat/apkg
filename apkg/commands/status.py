"""
show status of current project

usage: apkg status
"""

import os

from apkg import adistro
from apkg import log
from apkg.project import Project


def run_command(cargs):
    print_status()


def print_status():
    proj = Project()

    msg = "project base path:       {t.bold}{path}{t.normal}"
    print(msg.format(path=proj.path.resolve(), t=log.T))

    msg = "project config:          {t.bold}{path}{t.normal}"
    if proj.config_path.exists():
        msg += " ({t.green}exists{t.normal})"
    else:
        msg += " ({t.warn}doesn't exist{t.normal})"
    print(msg.format(path=proj.config_path, t=log.T))

    msg = "package templates path:  {t.bold}{path}{t.normal}"
    if proj.package_templates_path.exists():
        msg += " ({t.green}exists{t.normal})"
    else:
        msg += " ({t.red}doesn't exist{t.normal})"
    print(msg.format(path=proj.package_templates_path, t=log.T))

    print("package templates:")
    if proj.package_templates:
        msg_lines = []
        for template in proj.package_templates:
            short_path = os.path.join(*list(template.path.parts)[-3:])
            msg_lines.append("    {t.green}%s{t.normal}: {t.bold}%s{t.normal}"
                             % (template.package_style.name, short_path))
        msg = "\n".join(msg_lines)
    else:
        msg = "    {t.red}no package templates found{t.normal}"
    print(msg.format(dir=proj.package_templates_path, t=log.T))

    print()
    # distro status
    msg = "current distro: {t.cyan}{id}{t.normal} / {t.cyan}{full}{t.normal}"
    print(msg.format(full=adistro.fullname(), id=adistro.idver(), t=log.T))

    template = proj.get_package_template_for_distro(adistro.idver())
    msg = "    package style: "
    if template:
        style = template.package_style.name
        msg += "{t.green}%s{t.normal}" % style
    else:
        msg += "{t.warn}unsupported{t.normal}"
    print(msg.format(t=log.T))
    msg = "    package template: "
    if template:
        msg += "{t.green}%s{t.normal}" % template.path
    else:
        msg += "{t.warn}unsupported{t.normal}"
    print(msg.format(t=log.T))
