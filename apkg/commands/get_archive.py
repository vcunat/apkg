"""
download upstream archive for current project
using project.upstream_archive_url config option

Usage: apkg get-archive [-v <ver>] [--no-cache]

Options:
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
