"""
apkg package style for **Nix** (NixOS.org).

**source template:**
 - `default.nix` as-if in https://github.com/NixOS/nixpkgs
 - `top-level.nix` that simply wraps it to be buildable outside the official tree,
   in particular it should substitute the source archive;
   e.g. see ../../distro/pkg/nix/top-level.nix

**source package:** the same, just with templates substituted

**packages:** symlink(s) to your local nix store (see TODO)
"""
import re
import hashlib

from apkg import ex
from apkg.log import getLogger
from apkg.util.run import run
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


SUPPORTED_DISTROS = [
    'nix'
]

def fname_(path):
    return path / "default.nix"

def is_valid_template(path):
    return (path / "default.nix").exists() and (path / "top-level.nix").exists()

def get_template_name(path): # TODO: use `nix repl` instead?
    expr = fname_(path)
    for line in expr.open():
        m = re.match(r'\s*pname\s*=\s*"(\S+)";', line)
        if m:
            return m.group(1)

    raise ex.ParsingFailed(
        msg="unable to determine Name from: %s" % expr)

def get_srcpkg_nvr(path):
    # use source package parent dir as NVR
    return path.resolve().parent.name

# https://stackoverflow.com/a/44873382/587396
def sha256sum(filename):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

def build_srcpkg(
        build_path,
        out_path,
        archive_paths,
        template,
        env):
    archive_path = archive_paths[0]
    env = env or {}
    env['src_hash'] = sha256sum(archive_path)
    out_archive = out_path / archive_path.name
    log.info("applying templates")
    template.render(build_path, env or {})
    log.info("copying everything to: %s", out_path)
    shutil.copytree(build_path, out_path)
    shutil.copyfile(archive_path, out_archive)
    return [out_path / 'top-level.nix', out_path / 'default.nix', out_archive]
    # FIXME: list everything in the directory or what?

def build_packages(
        build_path,
        out_path,
        srcpkg_paths,
        **_):
    srcpkg_path = srcpkg_paths[0]
    log.info("building using nix (silent unless fails)") # TODO: perhaps without -L and shown?
    run('nix', 'build', '-f' , srcpkg_paths[0], '-o', out_path / 'result',
            '-L', # get full logs shown on failure
            '--keep-failed', # and keep the nix build dir for inspection
        )
    return [ ]
    # TODO: I'd use [ 'result' ] but that's (a symlink to) a directory and that breaks cache;
    # is there a point in producing some file?

