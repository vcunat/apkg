"""
shared apkg testing functions
"""
from pathlib import Path
import shutil

from apkg.compat import py35path


def init_testing_repo(repo_path, test_path):
    dst = Path(test_path) / Path(repo_path).name
    shutil.copytree(py35path(repo_path), py35path(dst))
    return dst
