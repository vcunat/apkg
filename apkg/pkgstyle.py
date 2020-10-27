"""
This is convenience interface to apkg.pkgstyles.* modules which can be
dynamically added because apkg.pkgstyles is PEP 420 namespace package.
"""
import importlib
import pkgutil
from pathlib import Path

import apkg.pkgstyles


def iter_package_styles():
    return pkgutil.iter_modules(
            apkg.pkgstyles.__path__,
            apkg.pkgstyles.__name__ + ".")


def import_package_styles():
    styles = {}
    for finder, modname, ispkg in iter_package_styles():
        _, _, name = modname.rpartition('.')
        module = importlib.import_module(modname)
        # insert package style name into module for convenience
        module.name = name
        styles[name] = module
    return styles


def get_package_template_style(path):
    for style in PACKAGE_STYLES.values():
        if style.is_valid_package_template(path):
            return style
    return None


def get_package_style_for_distro(distro):
    for style in PACKAGE_STYLES.values():
        if distro in style.SUPPORTED_DISTROS:
            return style
    return None


def get_package_style(style):
    return PACKAGE_STYLES.get(style)


PACKAGE_STYLES = import_package_styles()
