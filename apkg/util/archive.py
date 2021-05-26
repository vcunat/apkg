"""
apkg archive (tarball) utils
"""
from pathlib import Path

from apkg.parse import split_archive_fn, parse_version
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
    root_files_old = set(out_path.glob("*"))
    # shutil doesn't provide a way to check extracted files :(
    # pautil has bugs and got last release in 2016...
    shutil.unpack_archive(archive_path, out_path)
    root_files_new = set(out_path.glob("*"))
    root_files = root_files_new - root_files_old
    n_root_files = len(root_files)
    if n_root_files != 1:
        fmt = "Expected a single root dir but instead got %d files in root"
        raise ex.InvalidArchiveFormat(fmt=fmt % n_root_files)
    return root_files.pop()


def get_archive_version(archive_path):
    """
    return archive version detected from archive name
    """
    archive_path = Path(archive_path)
    _, _, ver, _ = split_archive_fn(archive_path.name)
    return parse_version(ver)
