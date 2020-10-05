"""
Show status of current project

Usage: apkg status

Options:
    TODO
"""

from docopt import docopt
import distro

from apkg import log


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)

    msg = "Detected distro: {t.bold_green}{distro}{t.normal}"
    print(msg.format(distro=" ".join(distro.linux_distribution()),
                     t=log.T))
