"""
create source package (files to build package from)

Usage: apkg srcpkg [-a <ar>] [-u]
                   [-v <ver>] [-r <rls>] [-d <distro>]
                   [--no-cache]

Options:
  -u, --upstream                  use upstream archive / apkg get-source
                                  default: use dev archvie / apkg make-source
  -a <ar>, --archive <ar>         use specified archive (path or name)
  -v <ver>, --version <ver>       set package version
  -r <rls>, --release <rls>       set package release
  -d <distro>, --distro <distro>  set target distro
                                  default: current distro
  --no-cache                      disable cache
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
            use_cache=not args['--no-cache'])
    print(out_srcpkg)
    return out_srcpkg
