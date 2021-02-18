"""
create source package (files to build package from)

Usage: apkg srcpkg [-u] [-a <ar>]
                   [-v <ver>] [-r <rls>] [-d <distro>]
                   [--no-cache] [--render-template]

Options:
  -u, --upstream                  upstream source package from archive
                                  default: dev source package from project
  -a <ar>, --archive <ar>         use specified archive (path or name)
  -v <ver>, --version <ver>       set package version
  -r <rls>, --release <rls>       set package release
  -d <distro>, --distro <distro>  set target distro
                                  default: current distro
  --no-cache                      disable cache
  --render-template               only render source package template
""" # noqa

from docopt import docopt

from apkg.lib import srcpkg


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    out_srcpkg = srcpkg.make_srcpkg(
            upstream=args['--upstream'],
            archive=args['--archive'],
            version=args['--version'],
            release=args['--release'],
            distro=args['--distro'],
            use_cache=not args['--no-cache'],
            render_template=args['--render-template'])
    print(out_srcpkg)
    return out_srcpkg
