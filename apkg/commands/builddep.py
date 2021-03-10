"""
ALIAS: apkg build-dep
"""
from apkg.cli import run_alias


def run_command(cargs):
    return run_alias('build-dep', cargs=cargs)
