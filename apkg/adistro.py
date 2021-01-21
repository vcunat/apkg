"""
distro-specific apkg helpers related to current distro

current distro info isn't going to change during run so cache that
"""
import re

import distro


def distro_arg(distro_str):
    """
    normalize --distro argument as used by CLI

    return current distro if not set
    """
    if distro_str:
        # convert custom distro string to idver format
        return distro2idver(distro_str)
    # use current distro by default
    return idver()


def distro2idver(distro_name):
    """
    convert generic distro string into idver format
    """
    return re.sub(r'\s+', '-', distro_name.strip().lower())


def idver():
    """
    return current distro in default idver format
    used by apkg to reference individual distros

    examples: debian-10, fedora-32, arch
    """
    global _idver
    if _idver is None:
        _idver = id()
        ver = version()
        if ver:
            _idver += "-%s" % (ver)
    return _idver


def fullname():
    """
    return human readable string describing current distro
    """
    global _fullname
    parts = [
        name(),
        distro.version(pretty=True),
    ]
    return " ".join([p for p in parts if p])


def id():  # pylint: disable=redefined-builtin
    global _id
    if _id is None:
        _id = distro.id()
    return _id


def name():
    global _name
    if _name is None:
        _name = distro.name()
    return _name


def codename():
    global _codename
    if _codename is None:
        _codename = distro.codename()
    return _codename


def version():
    global _version
    if _version is None:
        _version = distro.version()
    return _version


_id = None
_idver = None
_name = None
_codename = None
_version = None
_fullname = None
