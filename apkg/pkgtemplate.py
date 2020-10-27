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
        if out_path.exists():
            log.info("removing existing build dir: %s" % out_path)
            shutil.rmtree(out_path)
        log.info("renderding package template: %s -> %s", self.path, out_path)
        os.makedirs(out_path)

        for inf in os.scandir(self.path):
            inf_path = Path(inf)
            outf_path = out_path / inf_path.name
            log.info("rendering file: %s -> %s", inf_path, outf_path)

            t = None
            with inf_path.open('r') as inf:
                t = jinja2.Template(inf.read())
            with outf_path.open('w') as outf:
                outf.write(t.render(**vars))
