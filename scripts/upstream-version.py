#!/usr/bin/python3
"""
get latest upstream version from PyPI

This script can be used by apkg to check for latest upstream version
using upstream.version_script config option.
"""
from packaging.version import Version
import requests


def version_from_pypi(name):
    url = 'https://pypi.org/pypi/%s/json' % name
    r = requests.get(url)
    if not r.ok:
        return None
    data = r.json()

    versions = data['releases'].keys()
    version = sorted(versions, key=Version)[-1]

    return version


# apkg expects last stdout line to contain the upstream version string
print(version_from_pypi('apkg'))
