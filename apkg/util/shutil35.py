"""
A wrapper around selected shutil and os functions in order
to ensure compatibility with pathlib.Path in Python 3.5.

TODO: Once Python 3.5 support is dropped, replace all

    import apkg.util.shutil35 as shutil

with

    import shutil

and remove this compat module.
"""
import shutil
import os


def copy(src, dst, **kwargs):
    return shutil.copy(str(src), str(dst), **kwargs)


def copyfile(src, dst, **kwargs):
    return shutil.copyfile(str(src), str(dst), **kwargs)


def copytree(src, dst, **kwargs):
    return shutil.copytree(str(src), str(dst), **kwargs)


def rmtree(path, **kwargs):
    return shutil.rmtree(str(path), **kwargs)


def walk(top, **kwargs):
    return os.walk(str(top), **kwargs)
