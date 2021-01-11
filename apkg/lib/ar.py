"""
apkg lib for handling source archives
"""
import os
from pathlib import Path
import shutil
import jinja2
import requests

from apkg import exception
from apkg import log
from apkg.compat import py35path
from apkg.parse import split_archive_fn
from apkg.project import Project
from apkg.util.run import run


def make_archive(version=None, project=None):
    """
    create archive from current project state
    """
    log.bold("creating dev archive")
    proj = project or Project()
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
    log.info("archive created: %s" % archive_path)

    archive_fn = archive_path.name
    if version:
        # specific version requested - rename if needed
        name, sep, ver, ext = split_archive_fn(archive_fn)
        if ver != version:
            archive_fn = name + sep + version + ext
            msg = "archive renamed to match requested version: %s"
            log.info(msg, archive_fn)
    out_path = proj.dev_archive_path / archive_fn
    log.info("copying archive to: %s" % out_path)
    os.makedirs(py35path(proj.dev_archive_path), exist_ok=True)
    shutil.copy(py35path(archive_path), py35path(out_path))
    log.success("made archive: %s", out_path)
    return out_path


def get_archive(version=None, project=None):
    """
    download archive for current project
    """
    if not version:
        raise exception.ApkgException(
            "TODO: automatic latest version detection\n\n"
            "For now please select using --version/-v.")
    proj = project or Project()
    try:
        upstream_archive_url = proj.config['project']['upstream_archive_url']
    except KeyError:
        msg = ("get-archive requires project.upstream_archive_url option to\n"
               "be set in project config:\n\n"
               "%s" % proj.config_path)
        raise exception.MissingRequiredConfigOption(msg=msg)

    # variables available during templating
    env = {
        'project': proj,
        'version': version,
    }

    archive_t = jinja2.Template(upstream_archive_url)
    archive_url = archive_t.render(**env)
    log.info('downloading archive: %s', archive_url)
    r = requests.get(archive_url, allow_redirects=True)
    if not r.ok:
        raise exception.FileDownloadFailed(code=r.status_code, url=archive_url)
    _, _, archive_name = archive_url.rpartition('/')
    archive_path = proj.upstream_archive_path / archive_name
    log.info('saving archive to: %s', archive_path)
    os.makedirs(py35path(proj.upstream_archive_path), exist_ok=True)
    archive_path.open('wb').write(r.content)
    log.success('downloaded archive: %s', archive_path)

    try:
        upstream_signature_url = \
                proj.config['project']['upstream_signature_url']
    except KeyError:
        log.verbose("project.upstream_signature_url not set"
                    " - skipping signature download")
        return archive_path
    signature_t = jinja2.Template(upstream_signature_url)
    signature_url = signature_t.render(**env)
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
    if version:
        # optional version check requested
        if ver == version:
            log.verbose("archive name matches desired version: %s", version)
        else:
            msg = ("archive name doesn't match desired version: %s\n\n"
                   "desired version: %s\n"
                   "archive version: %s" % (archive_path.name, version, ver))
            raise exception.InvalidVersion(msg=msg)
    else:
        # no version was requested - use archive version
        version = ver
    return version


def archive_type(upstream=False):
    if upstream:
        return 'upstream'
    return 'dev'
