"""
Create dev archive from current project state

Usage: apkg make-archive
"""

from docopt import docopt
import os
from pathlib import Path
import shutil

from apkg import exception
from apkg import log
from apkg.project import Project
from apkg.util.cmd import run


def run_command(cargs):
    args = docopt(__doc__, argv=cargs)
    return make_archive()


def make_archive():
    proj = Project()
    try:
        script = proj.config['project']['make_archive_script']
    except KeyError:
        msg = ("make-archive requires project.make_archive_script option to\n"
        "be set in project config to a script that creates project\n"
        "archive and prints path to it on last stdout line.\n\n"
        "Please update project config with required information:\n\n"
        "%s" % proj.config_path)
        raise exception.MissingRequiredConfigOption(msg=msg)

    log.info("running make_archive_script: %s" % script)
    out = run(script)
    # last script stdout line is expected to be path to resulting archive
    _, _, last_line = out.rpartition('\n')
    archive_path = Path(last_line)
    if not archive_path.exists():
        msg = ("make_archive_script finished successfully but the archive\n"
               "(indicated by last script stdout line) doesn't exist:\n\n"
               "%s" % archive_path)
        raise exception.UnexpectedCommandOutput(msg=msg)
    else:
        log.info("archive created: %s" % archive_path)

    out_path = proj.dev_archive_path / archive_path.name
    log.info("copying archive to: %s" % out_path)
    os.makedirs(proj.dev_archive_path, exist_ok=True)
    shutil.copy(archive_path, out_path)
    log.info(log.T.green("archive ready ✓"))
    print(out_path)
