"""
download upstream archive for current project

upstream.archive_url config option specifies archive to download.

If upstream.signature_url config option is provided,
target signature file is downloaded alongside the archive.

When no --version is specified, apkg tries to detect latest version:

1) using upstream.version_script if set
2) from HTML listing if upstream.archive_url is set


Usage: apkg get-archive [-v <ver>] [-O <dir>] [--no-cache]

Options:
  -v, --version <ver>     version of archive to download
  -O, --result-dir <dir>  put results into specified dir
                          default: pkg/archive/upstream/
  --no-cache              disable cache
""" # noqa

from docopt import docopt

from apkg.lib import ar
from apkg.lib import common


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    results = ar.get_archive(
        version=args['--version'],
        result_dir=args['--result-dir'],
        use_cache=not args['--no-cache'])
    common.print_results(results)
    return results
