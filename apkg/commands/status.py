"""
show status of current project

Usage: apkg status
"""

from apkg.lib.status import status


def run_command(_):
    status()
