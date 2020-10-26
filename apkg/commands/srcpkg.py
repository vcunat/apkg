"""
ALIAS: apkg make-source-package
"""
from apkg.cli import run_alias


def run_command(cargs):
    return run_alias('make-source-package', cargs)
