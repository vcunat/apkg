"""
shared apkg testing functions
"""
import os
from pathlib import Path
import shutil

from apkg.compat import py35path


def init_testing_repo(repo_path, test_path):
    dst = Path(test_path) / Path(repo_path).name
    shutil.copytree(py35path(repo_path), py35path(dst))
    return dst


def inject_tree(src_path, dst_path):
    """
    copy all files from src_path into dst_path

    overwrite existing files
    """
    if not dst_path.exists():
        os.makedirs(py35path(dst_path), exist_ok=True)

    # recursively copy all files
    for d, _, files in os.walk(py35path(src_path)):
        rel_dir = Path(d).relative_to(src_path)
        dst_dir = dst_path / rel_dir
        os.makedirs(py35path(dst_dir), exist_ok=True)

        for fn in files:
            dst = dst_dir / fn
            src = Path(d) / fn
            shutil.copy(py35path(src), py35path(dst))
