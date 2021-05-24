"""
build packages

Usage: apkg build [-s | -a] [<file> | -F <file-list>]...
                  [-u] [-v <ver>] [-r <rls>] [-d <distro>]
                  [-O <dir>] [--no-cache]
                  [-i | -I]

Arguments:
  <file>                  specify input <file>s (when using -s or -a)
  -F, --file-list <fl>    specify text file listing one input file per line
                          use '-' to read from stdin

Options:
  -s, --srcpkg            build from source package <file>s
                          default: use srcpkg
  -a, --archive           build from archive <files>s
                          default: use make-archive (or get-archive in --upstream mode)
  -u, --upstream          build from upstream source package
                          default: build from dev source package
  -v, --version <ver>     set upstream archive version to use
                          implies --upstream, conflicts with --srcpkg and --archive
                          default: latest upstream version
  -r, --release <rls>     set package release
                          conflicts with --srcpkg
                          default: 1
  -d, --distro <distro>   set target distro
                          default: current distro
  -O, --result-dir <dir>  put results into specified dir
                          default: pkg/pkgs/DISTRO/NVR
  --no-cache              disable cache
  -i, --install-dep       install build dependencies on host (build-dep)
  -I, --isolated          use isolated builder (pbuilder, mock, ...)
                          default: use direct builder (rpmbuild, dpkg, makepkg, ...)
""" # noqa

from docopt import docopt

from apkg.lib import build
from apkg.util import common


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
