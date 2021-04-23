"""
build packages

Usage: apkg build [-u] [-s | -a] [<file> | -F <file-list>]...
                  [-v <ver>] [-r <rls>] [-d <distro>]
                  [-O <dir>] [--no-cache]
                  [-i | -I]

Arguments:
  <file>                  specify input <file>s (when using -s or -a)
  -F, --file-list <fl>    specify text file listing one input file per line
                          use '-' to read from stdin

Options:
  -u, --upstream          upstream build from archive
                          default: dev build from project
  -s, --srcpkg            build from source package <file>s
  -a, --archive           build from archive <files>s
  -v, --version <ver>     set package version
  -r, --release <rls>     set package release
  -d, --distro <distro>   set target distro
                          default: current distro
  -O, --result-dir <dir>  put results into specified dir
                          default: pkg/pkgs/DISTRO/NVR
  --no-cache              disable cache
  -i, --install-dep       install build dependencies on host (build-dep)
  -I, --isolated          use isolated builder (pbuilder, mock, ...)
                          default: use direct builder
""" # noqa

from docopt import docopt

from apkg.lib import build
from apkg.lib import common


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    results = build.build_package(
        upstream=args['--upstream'],
        srcpkg=args['--srcpkg'],
        archive=args['--archive'],
        input_files=args['<file>'],
        input_file_lists=args['--file-list'],
        version=args['--version'],
        release=args['--release'],
        distro=args['--distro'],
        result_dir=args['--result-dir'],
        install_dep=args['--install-dep'],
        isolated=args['--isolated'],
        use_cache=not args['--no-cache'])
    common.print_results(results)
    return results
