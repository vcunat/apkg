"""
create source package (files to build package from)

Usage: apkg srcpkg [-u] [-a <ar>]
                   [-v <ver>] [-r <rls>] [-d <distro>]
                   [-O <dir>]
                   [--no-cache] [--render-template]

Options:
  -u, --upstream                  upstream source package from archive
                                  default: dev source package from project
  -a <ar>, --archive <ar>         use specified archive (path or name)
  -v <ver>, --version <ver>       set package version
  -r <rls>, --release <rls>       set package release
  -d <distro>, --distro <distro>  set target distro
                                  default: current distro
  -O <dir>, --result-dir <dir>    put results into specified dir
                                  default: pkg/srcpkg/DISTRO/NVR
  --no-cache                      disable cache
  --render-template               only render source package template
""" # noqa

from docopt import docopt

from apkg.lib import srcpkg
from apkg.lib import common


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    results = srcpkg.make_srcpkg(
        upstream=args['--upstream'],
        archive=args['--archive'],
        version=args['--version'],
        release=args['--release'],
        distro=args['--distro'],
        result_dir=args['--result-dir'],
        use_cache=not args['--no-cache'],
        render_template=args['--render-template'])
    common.print_results(results)
    return results
