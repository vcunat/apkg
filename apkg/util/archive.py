"""
apkg archive (tarball) utils
"""
from pathlib import Path

from apkg import exception
from apkg.util.run import run


def unpack_archive(archive_path, out_path):
    """
    unpack supplied archive into out_path dir

    archive is expected to contain a single root dir

    return path to extracted root dir
    """
    def root_dir(ps):
        return Path(ps).parts[0]

    out_path.mkdir(parents=True, exist_ok=True)
    o = run('aunpack', '-X', out_path, archive_path)
    # parse output and make sure there's only a single root dir
    root_dirs = set(map(root_dir, o.split("\n")))
    n_root_files = len(root_dirs)
    if n_root_files != 1:
        fmt = "Expected a single root dir but insteat got %d files in root"
        raise exception.InvalidArchiveFormat(fmt=fmt % n_root_files)
    return out_path / root_dirs.pop()
