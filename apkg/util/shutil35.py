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


# this function copies upstream arg names 1:1
# pylint: disable=redefined-builtin
def unpack_archive(filename, extract_dir=None, format=None):
    # shutil supports pathlib starting with python 3.7
    if extract_dir:
        extract_dir = str(extract_dir)
    return shutil.unpack_archive(str(filename), extract_dir, format)
