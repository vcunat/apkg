"""
create dev archive from current project state

Use script specified by project.make_archive_script config option.


Usage: apkg make-archive [-v <ver>] [-O <dir>] [--no-cache]

Options:
  -v, --version <ver>     rename archive to match specified version if needed
  -O, --result-dir <dir>  put results into specified dir
                          default: pkg/archive/dev/
  --no-cache              disable cache
""" # noqa

from docopt import docopt

from apkg.lib import ar
from apkg.lib import common


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    results = ar.make_archive(
        version=args['--version'],
        result_dir=args['--result-dir'],
        use_cache=not args['--no-cache'])
    common.print_results(results)
    return results
