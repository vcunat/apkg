"""
integration tests for apkg
"""
from pathlib import Path
import pytest
import re
import subprocess


from apkg.util.run import cd
from apkg.util.git import git
from apkg.cli import apkg


APKG_REPO_URL = 'https://gitlab.nic.cz/packaging/apkg'
# pylint: disable=redefined-outer-name


@pytest.fixture(scope="module")
def clone_path(tmpdir_factory):
    """
    clone project repo once on module load and reuse it in individual tests
    """
    tmpd = tmpdir_factory.mktemp("apkg_test_apkg_git")
    p = '%s/apkg' % tmpd
    git('clone', APKG_REPO_URL, p)
    return Path(p)


@pytest.fixture(scope="module")
def repo_path(clone_path):
    """
    clone project repo and setup system for testing
    """
    with cd(clone_path):
        assert apkg('build-dep') == 0
    return clone_path


def test_apkg_full_pipe(repo_path):
    """
    test entire apkg pipeline using pipes

    This ensures:

    * apkg commands produce correct output
    * apkg commands are able to parse input from stdin (-F -)
    * apkg script is available from system shell

    Individual commands are tested in self tests.
    """
    with cd(repo_path):
        cmd = ('apkg make-archive'
               ' | apkg srcpkg -a -F -'
               ' | apkg build -s -F -'
               ' | apkg install -C -F -')
        code, out = subprocess.getstatusoutput(cmd)
    assert code == 0, "CMD ERROR (%s): %s" % (code, out)
    assert 'made archive:' in out
    assert 'made source package:' in out
    assert re.search(r'built \d+ packages', out)
    assert re.search(r'installed \d+ packages', out)
