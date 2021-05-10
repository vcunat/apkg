"""
apkg archive (tarball) utils
"""
from pathlib import Path

import apkg.util.shutil35 as shutil

from apkg import ex


def unpack_archive(archive_path, out_path):
    """
    unpack supplied archive into out_path dir

    archive is expected to contain a single root dir

    return path to extracted root dir
    """
    out_path = Path(out_path)
    out_path.mkdir(parents=True, exist_ok=True)
    shutil.unpack_archive(archive_path, out_path)
    # parse output and make sure there's only a single root dir
    root_files = list(out_path.glob("*"))
    n_root_files = len(root_files)
    if n_root_files != 1:
        fmt = "Expected a single root dir but instead got %d files in root"
        raise ex.InvalidArchiveFormat(fmt=fmt % n_root_files)
    return root_files[0]
