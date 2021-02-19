# -*- encoding: utf-8 -*-

import re
from packaging import version

from apkg.log import getLogger
from apkg.util.run import run


log = getLogger(__name__)


HTMLLISTPARSE_ERROR = None
try:
    import htmllistparse
except Exception as e:
    HTMLLISTPARSE_ERROR = e


RE_ARCHIVE_VERSION = r'[^\d]+-(.+)\.tar\..*'


def version_from_listing(html_listing_url):
    """
    get latest version from HTML listing
    """
    if HTMLLISTPARSE_ERROR:
        log.warning("unable to get upstream version from HTML listing: %s",
                    HTMLLISTPARSE_ERROR)
        return None
    log.verbose("getting upstream version from HTML listing: %s",
                html_listing_url)
    found = False
    v_max = version.parse('0')
    _, listing = htmllistparse.fetch_listing(
        html_listing_url, timeout=5)
    for f in listing:
        m = re.match(RE_ARCHIVE_VERSION, f.name)
        if not m:
            continue
        v = version.parse(m.group(1))
        v_max = max(v, v_max)
        found = True
    if found:
        return v_max
    return None


def version_from_script(script, script_name='script'):
    """
    get version from last stdout line of a script
    """
    log.verbose("getting upstream version from %s: %s", script_name, script)
    out = run(script)
    _, _, last_line = out.rpartition('\n')
    v = version.parse(last_line.strip())
    return v
