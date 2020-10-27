import re

from apkg import exception


# subgroups:
# 1) name
# 2) name-version separator ('-' or '_')
# 3) version (including release)
RE_NVR = r'^(.+?)([-_])(\d+(?:\.\d+)+(?:.+?)?)$'


def split_archive_fn(archive_fn):
    """
    split archive file name into individual parts

    return (name, separator, version, extension)
    """
    nvr, _, ext = archive_fn.rpartition('.')
    ext = '.%s' % ext
    if nvr.endswith('.tar'):
        nvr, _, _ = nvr.rpartition('.')
        ext = '.tar%s' % ext

    r = re.match(RE_NVR, nvr)
    if r:
        return r.groups() + (ext,)

    msg = "unable to parse version from archive file name: %s" % archive_fn
    raise exception.ParsingFailed(msg=msg)
