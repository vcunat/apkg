"""
Download upstream archive for current project

usage: apkg get-archive [-v <ver>] [--no-cache]

options:
  -v <ver>, --version <ver>  version of archive to download
  --no-cache                 disable cache
""" # noqa

from docopt import docopt

from apkg.lib import ar


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    out_path = ar.get_archive(
        version=args['--version'],
        use_cache=not args['--no-cache'])
    print(out_path)
    return out_path
