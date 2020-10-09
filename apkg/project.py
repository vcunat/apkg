import glob
from pathlib import Path
import sys
import os

from . import exception
from . import log
from . import pkgstyle


PACKAGE_TEMPLATES_DIR = 'distro'


class Project:
    """
    Project class serves as high level interface to projecs in need of
    packaging.
    """
    path = None
    package_templates_path = None

    package_templates = []

    def __init__(self, path=None):
        if path:
            self.path = path
        else:
            self.path = Path('.').resolve()
        self.load()

    def load(self):
        """
        Update project specific attributes for a project in self.path
        """
        self.package_templates_path = self.path / PACKAGE_TEMPLATES_DIR
        self.load_package_templates()

    def load_package_templates(self):
        if self.package_templates_path.exists():
            self.package_templates = load_package_templates(
                    self.package_templates_path)
        else:
            self.package_templates = []


def load_package_templates(path):
    package_templates = []
    for entry in os.scandir(path):
        if entry.is_dir():
            template_path = path / entry
            style, _ = pkgstyle.detect_packaging_template_style(template_path)
            if style:
                package_templates.append((template_path, style))
            else:
                log.verbose("Ignoring unknown packaging style in %s", template_path)
    return package_templates
