"""
shared apkg testing functions
"""
import os
from pathlib import Path
import shutil

from apkg.compat import py35path


def init_testing_repo(repo_path, test_path, ignore_dirs=[]):
    dst = Path(test_path) / Path(repo_path).name
    inject_tree(repo_path, dst, ignore_dirs=ignore_dirs)
    return dst


def inject_tree(src_path, dst_path, ignore_dirs=[]):
    """
    copy all files from src_path into dst_path

    overwrite existing files
    """
    if not dst_path.exists():
        os.makedirs(py35path(dst_path), exist_ok=True)

    # recursively copy all files
    for d, subdirs, files in os.walk(py35path(src_path)):
        if ignore_dirs:
            # ignore selected dirs
            ignored = []
            for sd in subdirs:
                if sd in ignore_dirs:
                    ignored.append(sd)
            for sd_ignore in ignored:
                subdirs.remove(sd_ignore)

        rel_dir = Path(d).relative_to(src_path)
        dst_dir = dst_path / rel_dir
        os.makedirs(py35path(dst_dir), exist_ok=True)

        for fn in files:
            dst = dst_dir / fn
            src = Path(d) / fn
            shutil.copy(py35path(src), py35path(dst))


def log_contains(string, caplog):
    for r in caplog.records:
        if string in r.message:
            return True
    return False
