"""
create source package (files to build packages from)

Usage: apkg srcpkg [-u] [-a] [<file> | -F <file-list>]...
                   [-v <ver>] [-r <rls>] [-d <distro>]
                   [-O <dir>] [--no-cache]
                   [--render-template]

Arguments:
  <file>                  specify input <file>s (when using -a/--archive)
  -F, --file-list <fl>    specify text file listing one input file per line
                          use '-' to read from stdin

Options:
  -u, --upstream          upstream source package from archive
                          default: dev source package from project
  -a, --archive           use specified archive <file>s
                          default: use project template
  -v, --version <ver>     set package version
  -r, --release <rls>     set package release
  -d, --distro <distro>   set target distro
                          default: current distro
  -O, --result-dir <dir>  put results into specified <dir>
                          default: pkg/srcpkg/DISTRO/NVR
  --no-cache              disable cache
  --render-template       only render source package template
                          default: create source package
""" # noqa

from docopt import docopt

from apkg.lib import srcpkg
from apkg.lib import common


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    results = srcpkg.make_srcpkg(
        upstream=args['--upstream'],
        archive=args['--archive'],
        input_files=args['<file>'],
        input_file_lists=args['--file-list'],
        version=args['--version'],
        release=args['--release'],
        distro=args['--distro'],
        result_dir=args['--result-dir'],
        use_cache=not args['--no-cache'],
        render_template=args['--render-template'])
    common.print_results(results)
    return results
