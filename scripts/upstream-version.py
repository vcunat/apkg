#!/usr/bin/python3
"""
example script to get latest upstream version from HTML file listing
and print it to stdout

Such custom script can be used by apkg to check for latest upstream version
using upstream.version_script config option.
"""
from apkg.util import upstreamversion


url = 'https://secure.nic.cz/files/knot-resolver/'
v = upstreamversion.version_from_listing(url)
print(v)
