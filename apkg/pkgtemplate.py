"""
module for handling and rendering apkg package templates
"""
from pathlib import Path
import jinja2

from apkg.log import getLogger
from apkg import pkgstyle as _pkgstyle
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


def default_render_filter(path):
    if str(path).endswith('.patch'):
        return False
    return True


class PackageTemplate:
    def __init__(self, path, style=None):
        self.path = Path(path)
        self.style = style

    @property
    def pkgstyle(self):
        if not self.style:
            self.style = _pkgstyle.get_pkgstyle_for_template(self.path)
        return self.style

    def render(self, out_path, env,
               render_filter=default_render_filter):
        """
        render package template into specified output directory
        """
        log.info("renderding package template: %s -> %s", self.path, out_path)
        if out_path.exists():
            log.verbose("template render dir exists: %s", out_path)
        else:
            out_path.mkdir(parents=True, exist_ok=True)

        # recursively render all files
        for d, _, files in shutil.walk(self.path):
            rel_dir = Path(d).relative_to(self.path)
            dst_dir = out_path / rel_dir
            dst_dir.mkdir(parents=True, exist_ok=True)

            for fn in files:
                dst = out_path / rel_dir / fn
                src = Path(d) / fn
                # TODO: filtering should be exposed through config files
                if render_filter(src):
                    log.verbose("rendering file: %s -> %s", src, dst)
                    t = None
                    with src.open('r') as srcf:
                        t = jinja2.Template(srcf.read())
                    with dst.open('w') as dstf:
                        dstf.write(t.render(**env) + '\n')
                else:
                    log.verbose(
                        "copying file without render: %s -> %s", src, dst)
                    shutil.copyfile(src, dst)
                # preserve original permission
                dst.chmod(src.stat().st_mode)
