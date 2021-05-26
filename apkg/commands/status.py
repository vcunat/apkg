import os

import click

from apkg import adistro
from apkg.log import getLogger, T
from apkg.project import Project


log = getLogger(__name__)


@click.command(name='status')
@click.help_option('-h', '--help', help='show this help')
def cli_status():
    """
    show status of current project
    """
    status()


def status():
    """
    show status of current project
    """
    proj = Project()

    msg = "project name:            {t.bold}{name}{t.normal}"
    print(msg.format(name=proj.name, t=T))
    msg = "project base path:       {t.bold}{path}{t.normal}"
    print(msg.format(path=proj.path.resolve(), t=T))

    msg = "project VCS:             {t.bold}{vcs}{t.normal}"
    print(msg.format(vcs=proj.vcs or 'none', t=T))

    msg = "project config:          {t.bold}{path}{t.normal}"
    if proj.config_path.exists():
        msg += " ({t.green}exists{t.normal})"
    else:
        msg += " ({t.warn}doesn't exist{t.normal})"
    print(msg.format(path=proj.config_path, t=T))

    msg = "package templates path:  {t.bold}{path}{t.normal}"
    if proj.templates_path.exists():
        msg += " ({t.green}exists{t.normal})"
    else:
        msg += " ({t.red}doesn't exist{t.normal})"
    print(msg.format(path=proj.templates_path, t=T))

    print("package templates:")
    if proj.templates:
        msg_lines = []
        for template in proj.templates:
            short_path = os.path.join(*list(template.path.parts)[-3:])
            msg_lines.append("    {t.green}%s{t.normal}: {t.bold}%s{t.normal}"
                             % (template.pkgstyle.name, short_path))
        msg = "\n".join(msg_lines)
    else:
        msg = "    {t.red}no package templates found{t.normal}"
    print(msg.format(dir=proj.templates_path, t=T))

    print()
    # distro status
    msg = "current distro: {t.cyan}{id}{t.normal} / {t.cyan}{full}{t.normal}"
    print(msg.format(full=adistro.fullname(), id=adistro.idver(), t=T))

    # we know what we're doing here
    # pylint: disable=protected-access
    template = proj._get_template_for_distro(adistro.idver())
    msg = "    package style: "
    if template:
        style = template.pkgstyle.name
        msg += "{t.green}%s{t.normal}" % style
    else:
        msg += "{t.warn}unsupported{t.normal}"
    print(msg.format(t=T))
    msg = "    package template: "
    if template:
        msg += "{t.green}%s{t.normal}" % template.path
    else:
        msg += "{t.warn}unsupported{t.normal}"
    print(msg.format(t=T))


APKG_CLI_COMMANDS = [cli_status]
