"""
generate docs from apkg code/docstrings using mkdocs-macros-plugin
"""
import inspect

from apkg import ex
from apkg import pkgstyle
from apkg.cli import cmd2mod
from pathlib import Path


BASE_PATH = Path(__file__).parent.parent
BASE_CODE_URL = "https://gitlab.nic.cz/packaging/apkg/-/blob/master/"
APKG_NEW_ISSUE_URL = "https://gitlab.nic.cz/packaging/apkg/-/issues/new"


def define_env(env):
    """
    this is available in docs using jinja2 templates
    """
    env.variables.pkgstyles = pkgstyle.PKGSTYLES
    env.variables.new_issue_url = APKG_NEW_ISSUE_URL
    env.variables.exceptions = get_exceptions()

    @env.filter
    def relpath(path):
        return Path(path).relative_to(BASE_PATH)

    @env.filter
    def file_link(path):
        return "[{fn}]({url}{fn})".format(
            fn=path.relative_to(BASE_PATH),
            url=BASE_CODE_URL)

    @env.filter
    def file_text(path):
        text = Path(path).open('r').read().strip()
        return "``` text\n%s\n```" % text

    @env.filter
    def mod_doc(modname):
        mod = __import__(modname, fromlist=[''])
        return mod.__doc__.strip()

    @env.filter
    def cmd_help(cmd):
        modname = 'apkg.commands.%s' % cmd2mod(cmd)
        return "``` text\n$> apkg %s --help\n\n%s\n```" % (
            cmd, mod_doc(modname))


def get_exceptions():
    """
    return all apkg exceptions sorted by exit_code
    """
    exs = [e for _, e in inspect.getmembers(ex, inspect.isclass)]
    exs.sort(key=lambda x: x.exit_code)
    return exs
