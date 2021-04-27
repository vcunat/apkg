"""
integration tests for Knot Resolver
"""
import glob
from pathlib import Path
import pytest
import apkg.util.shutil35 as shutil

from apkg.util import test
from apkg.util.run import cd
from apkg.util.git import git
from apkg.cli import apkg


KRESD_REPO_URL = 'https://gitlab.nic.cz/knot/knot-resolver'
KRESD_EXTRAS_DIR = Path(__file__).parent / 'data' / 'knot-resolver'


@pytest.fixture(scope="module")
def kresd_git(tmpdir_factory):
    """
    clone kresd repo once on module load and reuse it in individual tests
    using kresd_path

    don't use this directly in tests - use kresd_path instead for a fresh copy
    """
    # NOTE(py35): use tmp_path_factory once py3.5 is dropped
    tmpd = tmpdir_factory.mktemp("apkg_test_kresd_git")
    p = '%s/knot-resolver' % tmpd
    # NOTE: add --recursive to fetch submodules once needed
    git('clone', KRESD_REPO_URL, p)
    return Path(p)


@pytest.fixture(scope="function")
def kresd_path(kresd_git, tmpdir):
    """
    copy kresd_git into tmpdir for use in test
    """
    # NOTE(py35): use tmp_path once py3.5 is dropped
    p = '%s/knot-resolver' % tmpdir
    shutil.copytree(kresd_git, p, symlinks=True)
    return Path(p)


# pylint: disable=redefined-outer-name
def test_kresd_get_archive(kresd_path, capsys):
    VERSION = '5.2.0'
    repo_dir = str(kresd_path)
    assert repo_dir.endswith('knot-resolver')
    with cd(repo_dir):
        test.inject_tree(KRESD_EXTRAS_DIR, kresd_path)
        apkg('get-archive', '--version', VERSION)
        ar_files = glob.glob('pkg/archives/upstream/*')
    out, _ = capsys.readouterr()
    # expected output files
    archive_dst = "pkg/archives/upstream/knot-resolver-%s.tar.xz" % VERSION
    signature_dst = "%s.asc" % archive_dst
    # last stdout line should be downloaded archive
    assert archive_dst in out
    # make sure both archive and signature were downloaded into right path
    assert archive_dst in ar_files
    assert signature_dst in ar_files
