"""
Create dev archive from current project state

usage: apkg make-archive [-v <ver>]

options:
  -v <ver>, --version <ver>  rename archive to match specified version if needed
""" # noqa

from docopt import docopt

from apkg.lib import ar


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    out_path = ar.make_archive(version=args['--version'])
    print(out_path)
    return out_path
