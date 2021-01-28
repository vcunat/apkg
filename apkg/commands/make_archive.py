"""
Create dev archive from current project state

usage: apkg make-archive [-v <ver>] [--no-cache]

options:
  -v <ver>, --version <ver>  rename archive to match specified version if needed
  --no-cache                 disable cache
""" # noqa

from docopt import docopt

from apkg.lib import ar


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    out_path = ar.make_archive(
        version=args['--version'],
        use_cache=not args['--no-cache'])
    print(out_path)
    return out_path
