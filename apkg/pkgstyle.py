"""
This is convenience interface to apkg.pkgstyles.* modules which can be
dynamically added because apkg.pkgstyles is PEP 420 namespace package.
"""
import importlib
import pkgutil

import apkg.pkgstyles


def iter_pkgstyles():
    return pkgutil.iter_modules(
            apkg.pkgstyles.__path__,
            apkg.pkgstyles.__name__ + ".")


def import_pkgstyles():
    styles = {}
    for _, modname, _ in iter_pkgstyles():
        _, _, name = modname.rpartition('.')
        module = importlib.import_module(modname)
        # insert package style name into module for convenience
        module.name = name
        styles[name] = module
    return styles


def get_pkgstyle_for_template(path):
    for style in PKGSTYLES.values():
        if style.is_valid_template(path):
            return style
    return None


def get_pkgstyle_for_distro(distro):
    for style in PKGSTYLES.values():
        if distro in style.SUPPORTED_DISTROS:
            return style
    return None


def get_pkgstyle(style):
    return PKGSTYLES.get(style)


PKGSTYLES = import_pkgstyles()
