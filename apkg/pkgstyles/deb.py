"""
This is 'deb' apkg package style for Debian-based distros such as
Debian, Ubuntu, and their many clones.
"""
import glob
import os
from pathlib import Path
import re
import shutil

from apkg import log
from apkg import parse
from apkg.util.run import run, cd


SUPPORTED_DISTROS = [
    "ubuntu",
    "debian",
    "linuxmint",
    "raspbian",
    "scientific",
]


RE_PKG_NAME = r'Source:\s*(\S+)'


def is_valid_package_template(path):
    deb_files = ['rules', 'control', 'changelog']
    return all((path / f).exists() for f in deb_files)


def get_package_name(path):
    control = path / 'control'

    for line in control.open():
        m = re.match(RE_PKG_NAME, line)
        if m:
            return m.group(1)

    raise exception.ParsingFailed(
            msg="unable to determine Source from: %s" % pkgbuild)


def build_source_package(
        build_path,
        out_path,
        archive_path,
        package_template,
        vars):
    nv = "%s-%s" % (vars['name'], vars['version'])
    source_path = build_path / nv
    log.info("building deb source package: %s" % nv)
    log.info("unpacking archive: %s" % archive_path)
    os.makedirs(source_path)
    run('aunpack', '-X', build_path, archive_path)
    if not source_path.exists():
        # NOTE: if this happens oftern (it shouldn't), consider using
        #       atool's --save-outdir option above
        msg = ("archive unpack didn't result in expected dir: %s" % source_path)
        raise exception.UnexpectedCommandOutput(msg=msg)
    # render template
    debian_path = source_path / 'debian'
    package_template.render(debian_path, vars)
    # copy archive with debian .orig name
    _, _, _, ext = parse.split_archive_fn(archive_path.name)
    debian_ar = "%s_%s.orig%s" % (vars['name'], vars['version'], ext)
    debian_ar_path = build_path / debian_ar
    log.info("copying archive into source package: %s", debian_ar_path)
    shutil.copyfile(archive_path, debian_ar_path)

    log.info("building deb source-only package...")
    direct = bool(log.log.level <= log.INFO)
    with cd(source_path):
        run('dpkg-buildpackage', '-S', '-d', '-nc', '-sa', direct=direct)

    log.info("copying source package to result dir: %s", out_path)
    os.makedirs(out_path)
    for f in glob.iglob("%s/*" % build_path):
        src = Path(f)
        if not src.is_file():
            continue
        dst = out_path / src.relative_to(build_path)
        log.verbose("copying file to result dir: %s", dst)
        shutil.copyfile(src, dst)
