try:
    from functools import cached_property
except ImportError:
    from cached_property import cached_property
import glob
from pathlib import Path
import os
import toml

from apkg import log
from apkg import pkgtemplate


INPUT_BASE_DIR = 'distro'
OUTPUT_BASE_DIR = 'pkg'
CONFIG_FN = 'apkg.toml'


# pylint: disable=too-many-instance-attributes
# TODO: consider moving paths to project.path.* to address this warning
class Project:
    """
    Project class serves as high level interface to projecs in need of
    packaging
    """
    config = {}

    name = None
    path = None
    package_templates_path = None
    config_base_path = None
    config_path = None
    archive_path = None
    dev_archive_path = None
    upstream_archive_path = None
    build_path = None
    package_build_path = None
    srcpkg_build_path = None
    package_out_path = None
    srcpkg_out_path = None

    def __init__(self, path=None, autoload=True):
        if path:
            self.path = path
        else:
            self.path = Path('.')
        if autoload:
            self.load()

    def update_attrs(self):
        """
        update project attributes based on current config
        """
        self.name = self.config.get('project', {}).get('name')
        if self.name:
            log.verbose("project name from config: %s" % self.name)
        else:
            self.name = self.path.resolve().name
            log.verbose("project name not in config - "
                        "guessing from path: %s", self.name)

    def update_paths(self):
        """
        fill in projects paths based on current self.path and self.config
        """
        # package templates: distro/pkg
        self.package_templates_path = self.path / INPUT_BASE_DIR / 'pkg'
        # archives: pkg/archives
        self.archive_path = self.path / OUTPUT_BASE_DIR / 'archives'
        self.dev_archive_path = self.archive_path / 'dev'
        self.upstream_archive_path = self.archive_path / 'upstream'
        # build: pkg/build
        self.build_path = self.path / OUTPUT_BASE_DIR / 'build'
        self.package_build_path = self.build_path / 'pkgs'
        self.srcpkg_build_path = self.build_path / 'srcpkgs'
        # output: pkg/{src-,}package
        self.package_out_path = self.path / OUTPUT_BASE_DIR / 'pkgs'
        self.srcpkg_out_path = self.path / OUTPUT_BASE_DIR / 'srcpkgs'

    def load(self):
        """
        load project config and update its attributes
        """
        self.config_base_path = self.path / INPUT_BASE_DIR / 'config'
        self.config_path = self.config_base_path / CONFIG_FN
        self.load_config()
        self.update_attrs()
        self.update_paths()

    def load_config(self):
        if self.config_path.exists():
            log.verbose("loading project config: %s" % self.config_path)
            self.config = toml.load(self.config_path.open())
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

    def get_package_template_for_distro(self, distro):
        # NOTE: this is very simplistic, more complex mechanism TBD
        ldistro = distro.lower()
        for t in self.package_templates:
            ps = t.package_style
            for d in ps.SUPPORTED_DISTROS:
                if d in ldistro:
                    return t
        return None

    def find_archives_by_name(self, name, upstream=False):
        """
        find archive files with supplied name in expected project paths
        """
        if upstream:
            ar_path = self.upstream_archive_path
        else:
            ar_path = self.dev_archive_path
        return glob.glob("%s/%s*" % (ar_path, name))


def load_package_templates(path):
    package_templates = []
    for entry_path in glob.glob('%s/*' % path):
        if os.path.isdir(entry_path):
            template = pkgtemplate.PackageTemplate(entry_path)
            if template.package_style:
                package_templates.append(template)
            else:
                log.warn("ignoring unknown package style in %s", entry_path)
    return package_templates
