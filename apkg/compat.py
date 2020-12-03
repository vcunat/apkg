"""
python version compatibility helpers
"""
import sys


# python 3.5 doesn't have pathlib fully integrated so str() conversion is
# needed in some places - use py35path() for easy removal later
if sys.version_info.minor <= 5:
    def py35path(s):
        return str(s)
else:
    def py35path(s):
        return s
