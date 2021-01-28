try:
    from functools import cached_property
except ImportError:
    from cached_property import cached_property
import glob
import hashlib
from pathlib import Path
import os
import toml

from apkg import cache as _cache
from apkg import exception
from apkg.log import getLogger
from apkg import pkgtemplate
from apkg.util.git import git


log = getLogger(__name__)


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
    templates_path = None
    cache_path = None
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
        self.cache = _cache.ProjectCache(self)

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
        self.templates_path = self.path / INPUT_BASE_DIR / 'pkg'
        # archives: pkg/archives/{dev,upstream}
        self.archive_path = self.path / OUTPUT_BASE_DIR / 'archives'
        self.dev_archive_path = self.archive_path / 'dev'
        self.upstream_archive_path = self.archive_path / 'upstream'
        # build: pkg/build/{src-,}pkg
        self.build_path = self.path / OUTPUT_BASE_DIR / 'build'
        self.package_build_path = self.build_path / 'pkgs'
        self.srcpkg_build_path = self.build_path / 'srcpkgs'
        # output: pkg/{src-,}pkg
        self.package_out_path = self.path / OUTPUT_BASE_DIR / 'pkgs'
        self.srcpkg_out_path = self.path / OUTPUT_BASE_DIR / 'srcpkgs'
        # cache: pkg/.cache.json
        self.cache_path = self.path / OUTPUT_BASE_DIR / '.cache.json'

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
    def vcs(self):
        """
        Version Control System used in project

        possible outputs: 'git', None
        """
        o = git('rev-parse', silent=True, fatal=False)
        if o.return_code == 0:
            return 'git'
        return None

    @cached_property
    def checksum(self):
        """
        checksum of current project state

        requires VCS (git), only computed once
        """
        if self.vcs == 'git':
            checksum = git.current_commit()[:10]
            diff = git('diff', log_cmd=False)
            if diff:
                diff_hash = hashlib.sha256(diff.encode('utf-8'))
                checksum += '-%s' % diff_hash.hexdigest()[:10]
            return checksum
        return None

    @cached_property
    def templates(self):
        if self.templates_path.exists():
            return load_templates(self.templates_path)
        else:
            return []

    def _get_template_for_distro(self, distro):
        for t in self.templates:
            ps = t.pkgstyle
            for d in ps.SUPPORTED_DISTROS:
                # NOTE: this is very simplistic
                if d in distro:
                    return t
        return None

    def get_template_for_distro(self, distro):
        ldistro = distro.lower()
        template = self._get_template_for_distro(ldistro)
        if not template:
            tdir = self.templates_path
            msg = ("missing package template for distro: %s\n\n"
                   "you can add it into: %s" % (distro, tdir))
            raise exception.MissingPackagingTemplate(msg=msg)
        return template

    def find_archives_by_name(self, name, upstream=False):
        """
        find archive files with supplied name in expected project paths
        """
        if upstream:
            ar_path = self.upstream_archive_path
        else:
            ar_path = self.dev_archive_path
        return glob.glob("%s/%s*" % (ar_path, name))


def load_templates(path):
    templates = []
    for entry_path in glob.glob('%s/*' % path):
        if os.path.isdir(entry_path):
            template = pkgtemplate.PackageTemplate(entry_path)
            if template.pkgstyle:
                templates.append(template)
            else:
                log.warning("ignoring unknown package style in %s", entry_path)
    return templates
