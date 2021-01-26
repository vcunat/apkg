"""
module for handling and rendering apkg package templates
"""
import os
from pathlib import Path
import jinja2

from apkg.compat import py35path
from apkg.log import getLogger
from apkg import pkgstyle as _pkgstyle


log = getLogger(__name__)


class PackageTemplate:
    def __init__(self, path, style=None):
        self.path = Path(path)
        self.style = style

    @property
    def pkgstyle(self):
        if not self.style:
            self.style = _pkgstyle.get_pkgstyle_for_template(self.path)
        return self.style

    def render(self, out_path, env):
        """
        render package template into specified output directory
        """
        log.info("renderding package template: %s -> %s", self.path, out_path)
        if out_path.exists():
            log.verbose("template render dir exists: %s" % out_path)
        else:
            os.makedirs(py35path(out_path), exist_ok=True)

        # recursively render all files
        for d, _, files in os.walk(py35path(self.path)):
            rel_dir = Path(d).relative_to(self.path)
            dst_dir = out_path / rel_dir
            os.makedirs(py35path(dst_dir), exist_ok=True)

            for fn in files:
                dst = out_path / rel_dir / fn
                src = Path(d) / fn
                log.verbose("rendering file: %s -> %s", src, dst)
                t = None
                with src.open('r') as srcf:
                    t = jinja2.Template(srcf.read())
                with dst.open('w') as dstf:
                    dstf.write(t.render(**env) + '\n')
