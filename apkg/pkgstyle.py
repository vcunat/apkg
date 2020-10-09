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


def import_packaging_styles():
    styles = {}
    for finder, modname, ispkg in iter_pkgstyles():
        _, _, name = modname.rpartition('.')
        module = importlib.import_module(modname)
        styles[name] = module
    return styles


def detect_packaging_template_style(path):
    for name, style in PACKAGING_STYLES.items():
        if style.is_valid_packaging_template(path):
            return name, style
    return None, None


def get_packaging_style_for_distro(distro):
    for name, style in PACKAGING_STYLES.items():
        if distro in style.SUPPORTED_DISTROS:
            return name, style
    return None, None


PACKAGING_STYLES = import_packaging_styles()
