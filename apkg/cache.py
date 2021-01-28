"""
apkg packaging file cache
"""

import hashlib
import json
from pathlib import Path

from apkg.compat import py35path
from apkg.log import getLogger


log = getLogger(__name__)


def file_checksum(path):
    chsum = hashlib.sha256()
    with open(py35path(path), "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            chsum.update(chunk)
    return chsum.hexdigest()[:20]


class ProjectCache:
    def __init__(self, project):
        self.project = project
        self.loaded = False
        self.cache = {}
        self.checksum = None

    def save(self):
        json.dump(self.cache, self.project.cache_path.open('w'))

    def load(self):
        cache_path = self.project.cache_path
        if not cache_path.exists():
            log.verbose("cache not found: %s", cache_path)
            return
        log.verbose("loading cache: %s", cache_path)
        self.cache = json.load(self.project.cache_path.open('r'))

    def _ensure_load(self):
        """
        ensure cache is loaded on demand and only once

        you don't need to call this directly
        """
        if self.loaded:
            return
        self.load()
        self.loaded = True

    def update(self, cache_name, key, path):
        assert key
        log.verbose("cache update for %s: %s -> %s",
                    cache_name, key, path)
        self._ensure_load()
        if cache_name not in self.cache:
            self.cache[cache_name] = {}
        entry = self.path2entry(path)
        self.cache[cache_name][key] = entry
        self.save()

    def get(self, cache_name, key):
        log.verbose("cache query for %s: %s",
                    cache_name, key)

        def validate(path, checksum):
            if not path.exists():
                log.info("removing missing file from cache: %s", path)
                self.delete(cache_name, key)
                return False
            real_checksum = file_checksum(path)
            if real_checksum != checksum:
                log.info("removing invalid cache entry: %s", path)
                self.delete(cache_name, key)
                return False
            return True

        self._ensure_load()
        entry = self.cache.get(cache_name, {}).get(key)
        if not entry:
            return None
        path = self.entry2path(entry, validate_fun=validate)
        return path

    def delete(self, cache_name, key):
        self.cache[cache_name].pop(key, None)
        self.save()

    def path2entry(self, path):
        """
        convert path or a list of paths to corresponding cache entry

        return (fn, checksum) or a list of that on multiple paths
        """
        is_list = True
        if not isinstance(path, list):
            path = [path]
            is_list = False

        e = list(map(
            lambda x: (str(x), file_checksum(x)),
            path))
        if is_list:
            return e
        return e[0]

    def entry2path(self, entry, validate_fun=None):
        """
        convert cache entry to file path or list of paths

        if validate is True, make sure file has correct checksum
        and flush invalid cache entry if it doesn't
        """
        is_list = True
        if not isinstance(entry[0], list):
            entry = [entry]
            is_list = False

        paths = []
        for fn, checksum in entry:
            p = Path(fn)
            if validate_fun:
                if not validate_fun(p, checksum):
                    return None
            paths.append(p)

        if is_list:
            return paths
        return paths[0]

    def enabled(self, use_cache=True):
        """
        helper to tell and log if caching is enabled and supported

        optional use_cache argument provided for shared
        argument parsing and logging from apkg.lib
        """
        if use_cache:
            vcs = self.project.vcs
            if vcs:
                log.verbose("%s VCS detected -> cache ENABLED", vcs)
                return True
            else:
                log.verbose("VCS not detected -> cache DISABLED")
        else:
            log.verbose("cache DISABLED")
        return False
