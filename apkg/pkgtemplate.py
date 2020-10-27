"""
module for handling and rendering apkg package templates
"""
import jinja2
from pathlib import Path
import os
import shutil

from apkg import exception
from apkg import log
from apkg import pkgstyle


class PackageTemplate:
    def __init__(self, path, package_style=None):
        self.path = Path(path)
        self.style = package_style

    @property
    def package_style(self):
        if not self.style:
            self.style = pkgstyle.get_package_template_style(self.path)
        return self.style

    def render(self, out_path, vars):
        """
        render package template into specified output directory
        """
        log.info("renderding package template: %s -> %s", self.path, out_path)
        if out_path.exists():
            log.verbose("template render dir exists: %s" % out_path)
        else:
            os.makedirs(out_path, exist_ok=True)

        # recursively render all files
        for dir, subdirs, files in os.walk(self.path):
            rel_dir = Path(dir).relative_to(self.path)
            dst_dir = out_path / rel_dir
            os.makedirs(dst_dir, exist_ok=True)

            for fn in files:
                dst = out_path / rel_dir / fn
                src = Path(dir) / fn
                log.verbose("rendering file: %s -> %s", src, dst)
                t = None
                with src.open('r') as srcf:
                    t = jinja2.Template(srcf.read())
                with dst.open('w') as dstf:
                    dstf.write(t.render(**vars) + '\n')
