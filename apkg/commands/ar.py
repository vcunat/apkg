"""
ALIAS: apkg make-archive
"""
from apkg.cli import run_alias


def run_command(cargs):
    return run_alias('make-archive', cargs=cargs)
