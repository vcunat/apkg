from pathlib import Path
import re

from apkg.util import test
from apkg.util.run import cd
from apkg.cli import apkg


APKG_BASE_DIR = Path(__file__).parents[2]


# NOTE(py35): use tmp_path instead of tmpdir
#             when py3.5 support is dropped


def test_apkg_make_archive(tmpdir, capsys):
    repo_path = test.init_testing_repo(APKG_BASE_DIR, str(tmpdir))
    repo_dir = str(repo_path)
    assert repo_dir.endswith('apkg')
    with cd(repo_dir):
        assert apkg('make-archive') == 0
    out, _ = capsys.readouterr()
    # last stdout line should be resulting archive
    assert re.search(r"pkg/archives/dev/apkg-.*\.tar\.gz$", out)


def test_apkg_get_archive(tmpdir, capsys):
    VERSION = '0.0.1'
    repo_path = test.init_testing_repo(APKG_BASE_DIR, str(tmpdir))
    repo_dir = str(repo_path)
    assert repo_dir.endswith('apkg')
    with cd(repo_dir):
        assert apkg('get-archive', '--version', VERSION) == 0
    out, _ = capsys.readouterr()
    # last stdout line should be downloaded archive
    assert ("pkg/archives/upstream/apkg-v%s.tar.gz" % VERSION) in out


def test_apkg_srcpkg(tmpdir, capsys):
    repo_path = test.init_testing_repo(APKG_BASE_DIR, str(tmpdir))
    repo_dir = str(repo_path)
    assert repo_dir.endswith('apkg')
    with cd(repo_dir):
        assert apkg('srcpkg') == 0
    out, _ = capsys.readouterr()
    # last stdout line should be resulting source package
    assert re.search(r"pkg/srcpkgs/\S+/apkg\S+$", out)


def test_apkg_build(tmpdir, capsys):
    repo_path = test.init_testing_repo(APKG_BASE_DIR, str(tmpdir))
    repo_dir = str(repo_path)
    assert repo_dir.endswith('apkg')
    with cd(repo_dir):
        assert apkg('build') == 0
    out, _ = capsys.readouterr()
    # last line should be one of resulting packages
    assert re.search(r"pkg/pkgs/\S+/apkg\S+$", out)
