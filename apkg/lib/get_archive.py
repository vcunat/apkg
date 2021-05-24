"""
apkg lib for handling (upstream) source archive download
"""
from pathlib import Path
import re
import requests

from apkg import ex
from apkg.util import common
from apkg.log import getLogger
from apkg.project import Project


log = getLogger(__name__)


def get_archive(
        version=None,
        result_dir=None,
        use_cache=True,
        project=None):
    """
    download archive for current project
    """
    proj = project or Project()
    if not version:
        version = proj.upstream_version
        if not version:
            raise ex.UnableToDetectUpstreamVersion()
    archive_url = proj.upstream_archive_url(version)

    use_cache = proj.cache.enabled(use_cache)
    if use_cache:
        cache_name = 'archive/upstream'
        cache_key = archive_url
        cached = common.get_cached_paths(
            proj, cache_name, cache_key, result_dir)
        if cached:
            log.success("reuse cached archive: %s", cached[0])
            return cached

    log.info('downloading archive: %s', archive_url)

    _, _, archive_fn = archive_url.rpartition('/')
    if result_dir:
        ar_base_path = Path(result_dir)
    else:
        ar_base_path = proj.upstream_archive_path

    r = requests.get(archive_url, allow_redirects=True)
    if r.status_code != 200:
        raise ex.FileDownloadFailed(code=r.status_code, url=archive_url)
    content_type = r.headers.get('content-type', '')
    if not content_type.startswith('application/'):
        msg = 'Failed to download archive - invalid content-type "%s":\n\n%s'
        raise ex.FileDownloadFailed(
            msg=msg % (content_type, archive_url))

    content_disp = r.headers.get('content-disposition')
    if content_disp:
        m = re.search(r'filename=(.+)', content_disp)
        if m:
            archive_fn = m.group(1).strip(' "')
            log.verbose("archive file name from HTTP Content-Disposition: %s",
                        archive_fn)

    archive_path = ar_base_path / archive_fn
    log.info('saving archive to: %s', archive_path)
    ar_base_path.mkdir(parents=True, exist_ok=True)
    archive_path.open('wb').write(r.content)
    log.success('downloaded archive: %s', archive_path)
    results = [archive_path]

    signature_url = proj.upstream_signature_url(version)
    if signature_url:
        # singature check
        log.info('downloading signature: %s', signature_url)
        r = requests.get(signature_url, allow_redirects=True)
        if not r.ok:
            raise ex.FileDownloadFailed(
                code=r.status_code, url=signature_url)
        _, _, signature_name = signature_url.rpartition('/')
        signature_path = ar_base_path / signature_name
        log.info('saving signature to: %s', signature_path)
        signature_path.open('wb').write(r.content)
        log.success('downloaded signature: %s', signature_path)
        results.append(signature_path)
    else:
        log.verbose("project.upstream_signature_url not set"
                    " - skipping signature download")

    if use_cache:
        proj.cache.update(
            cache_name, cache_key, results)

    return results
