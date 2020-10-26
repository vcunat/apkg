from functools import cached_property
from pathlib import Path
import sys
import os
import toml

from . import exception
from . import log
from . import pkgstyle


INPUT_BASE_DIR = 'distro'
OUTPUT_BASE_DIR = 'pkg'
CONFIG_FN = 'apkg.toml'


class Project:
    """
    Project class serves as high level interface to projecs in need of
    packaging
    """
    config = {}
    package_templates = []

    path = None
    package_templates_path = None
    config_base_path = None
    config_path = None
    archives_path = None
    dev_archive_path = None
    upstream_archive_path = None

    def __init__(self, path=None, autoload=True):
        if path:
            self.path = path
        else:
            self.path = Path('.')
        if autoload:
            self.load()

    def construct_paths(self):
        """
        fill in projects paths based on current self.path and self.config
        """
        # package templates: distro/pkg
        self.package_templates_path = self.path / INPUT_BASE_DIR / 'pkg'
        if not self.package_templates_path.exists():
            # TODO: This is a temporary backward compat bridge.
            #       Remove this as soon as knot projects use distro/pkg.
            legacy_path = self.path / INPUT_BASE_DIR
            if legacy_path.exists():
                log.warn("package templates path doesn't exist: %s\n"
                         "using legacy templates path (TO BE REMOVED): %s"
                         % (self.package_templates_path, legacy_path))
                self.package_templates_path = legacy_path
        # archives: pkg/archives
        self.archive_path = self.path / OUTPUT_BASE_DIR / 'archives'
        self.dev_archive_path = self.archive_path / 'dev'
        self.upstream_archive_path = self.archive_path / 'upstream'


    def load(self):
        """
        load project config and update its attributes
        """
        self.config_base_path = self.path / INPUT_BASE_DIR / 'config'
        self.config_path = self.config_base_path / CONFIG_FN
        self.load_config()
        self.construct_paths()

    def load_config(self):
        if self.config_path.exists():
            log.verbose("loading project config: %s" % self.config_path)
            self.config = toml.load(self.config_path)
            return True
        else:
            log.verbose("project config not found: %s" % self.config_path)
            return False

    @cached_property
    def package_templates(self):
        if self.package_templates_path.exists():
            return load_package_templates(self.package_templates_path)
        else:
            return []


def load_package_templates(path):
    package_templates = []
    for entry in os.scandir(path):
        if entry.is_dir():
            template_path = Path(entry)
            style, _ = pkgstyle.detect_packaging_template_style(template_path)
            if style:
                package_templates.append((template_path, style))
            else:
                log.verbose("ignoring unknown packaging style in %s", template_path)
    return package_templates
