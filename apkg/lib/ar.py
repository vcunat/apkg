"""
apkg lib for handling source archives
"""
import os
from pathlib import Path
import shutil
import requests

from apkg import exception
from apkg.log import getLogger
from apkg.compat import py35path
from apkg.parse import split_archive_fn, parse_version
from apkg.project import Project
from apkg.util.run import run


log = getLogger(__name__)


def make_archive(version=None, project=None, use_cache=True):
    """
    create archive from current project state
    """
    log.bold("creating dev archive")
    proj = project or Project()
    use_cache = proj.cache.enabled(use_cache)
    if use_cache:
        archive_path = proj.cache.get('archive/dev', proj.checksum)
        if archive_path:
            log.success("reuse cached archive: %s", archive_path)
            return archive_path
    script = proj.config_get('project.make_archive_script')
    if not script:
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
    in_archive_path = Path(last_line)
    if not in_archive_path.exists():
        msg = ("make_archive_script finished successfully but the archive\n"
               "(indicated by last script stdout line) doesn't exist:\n\n"
               "%s" % in_archive_path)
        raise exception.UnexpectedCommandOutput(msg=msg)
    log.info("archive created: %s" % in_archive_path)

    archive_fn = in_archive_path.name
    if version:
        # specific version requested - rename if needed
        name, sep, ver, ext = split_archive_fn(archive_fn)
        if parse_version(ver) != version:
            archive_fn = name + sep + version + ext
            msg = "archive renamed to match requested version: %s"
            log.info(msg, archive_fn)
    archive_path = proj.dev_archive_path / archive_fn
    log.info("copying archive to: %s" % archive_path)
    os.makedirs(py35path(proj.dev_archive_path), exist_ok=True)
    shutil.copy(py35path(in_archive_path), py35path(archive_path))
    log.success("made archive: %s", archive_path)
    if use_cache:
        proj.cache.update(
            'archive/dev', proj.checksum, str(archive_path))
    return archive_path


def get_archive(version=None, project=None, use_cache=True):
    """
    download archive for current project
    """
    proj = project or Project()
    if not version:
        version = proj.upstream_version
        if not version:
            raise exception.UnableToDetectUpstreamVersion()
    use_cache = proj.cache.enabled(use_cache)
    archive_url = proj.upstream_archive_url(version)

    if use_cache:
        archive_path = proj.cache.get('archive/upstream', archive_url)
        if archive_path:
            log.success("reuse cached archive: %s", archive_path)
            return archive_path

    log.info('downloading archive: %s', archive_url)
    r = requests.get(archive_url, allow_redirects=True)
    if r.status_code != 200:
        raise exception.FileDownloadFailed(code=r.status_code, url=archive_url)
    content_type = r.headers['content-type']
    if not content_type.startswith('application/'):
        msg = 'Failed to download archive - invalid content-type "%s":\n\n%s'
        raise exception.FileDownloadFailed(
            msg=msg % (content_type, archive_url))

    _, _, archive_name = archive_url.rpartition('/')
    archive_path = proj.upstream_archive_path / archive_name
    log.info('saving archive to: %s', archive_path)
    os.makedirs(py35path(proj.upstream_archive_path), exist_ok=True)
    archive_path.open('wb').write(r.content)
    log.success('downloaded archive: %s', archive_path)

    if use_cache:
        proj.cache.update(
            'archive/upstream', archive_url, str(archive_path))

    signature_url = proj.upstream_signature_url(version)
    if not signature_url:
        log.verbose("project.upstream_signature_url not set"
                    " - skipping signature download")
        return archive_path
    # singature check
    log.info('downloading signature: %s', signature_url)
    r = requests.get(signature_url, allow_redirects=True)
    if not r.ok:
        raise exception.FileDownloadFailed(
                code=r.status_code, url=signature_url)
    _, _, signature_name = signature_url.rpartition('/')
    signature_path = proj.upstream_archive_path / signature_name
    log.info('saving signature to: %s', signature_path)
    signature_path.open('wb').write(r.content)
    log.success('downloaded signature: %s', signature_path)

    return archive_path


def find_archive(archive, upstream=False, project=None):
    """
    find archive in project path and check/return its version
    """
    ar_path = Path(archive)
    if not ar_path.exists():
        ar_type = archive_type(upstream=upstream)
        if not project:
            project = Project()
        ars = project.find_archives_by_name(archive, upstream=upstream)
        if not ars:
            raise exception.ArchiveNotFound(ar=archive, type=ar_type)
        if len(ars) > 1:
            msg = ("multiple matching %s archives found - "
                   "not sure which one to use:\n" % ar_type)
            for ar in ars:
                msg += "\n%s" % ar
            raise exception.ArchiveNotFound(msg=msg)
        ar_path = Path(ars[0])

        log.verbose("found %s archive: %s", ar_type, ar_path)

    return ar_path


def get_archive_version(archive_path, version=None):
    """
    return archive version detected from archive name

    if version is specified, ensure it matches archive version
    """
    archive_path = Path(archive_path)
    _, _, ver, _ = split_archive_fn(archive_path.name)
    ar_ver = parse_version(ver)
    if version:
        # optional version check requested
        if ar_ver == version:
            log.verbose("archive name matches desired version: %s", version)
        else:
            msg = ("archive name doesn't match desired version: %s\n\n"
                   "desired version: %s\n"
                   "archive version: %s" % (archive_path.name, version, ver))
            raise exception.InvalidVersion(msg=msg)
    else:
        # no version was requested - use archive version
        version = ar_ver
    return version


def archive_type(upstream=False):
    if upstream:
        return 'upstream'
    return 'dev'
