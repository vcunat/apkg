from pathlib import Path
import os
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
    # first stdout line should be resulting archive
    assert re.match(r"pkg/archives/dev/apkg-.*\.tar\.gz", out)


def test_apkg_get_archive(tmpdir, capsys):
    VERSION = '0.0.1'
    repo_path = test.init_testing_repo(APKG_BASE_DIR, str(tmpdir))
    repo_dir = str(repo_path)
    assert repo_dir.endswith('apkg')
    with cd(repo_dir):
        assert apkg('get-archive', '--version', VERSION) == 0
    out, _ = capsys.readouterr()
    # first stdout line should be downloaded archive
    assert out.startswith("pkg/archives/upstream/apkg-v%s.tar.gz" % VERSION)


def test_apkg_srcpkg(tmpdir, capsys):
    repo_path = test.init_testing_repo(APKG_BASE_DIR, str(tmpdir))
    repo_dir = str(repo_path)
    assert repo_dir.endswith('apkg')
    with cd(repo_dir):
        assert apkg('srcpkg') == 0
    out, _ = capsys.readouterr()
    # first stdout line should be resulting source package
    assert re.match(r"pkg/srcpkgs/\S+/apkg\S+", out)


def test_apkg_build(tmpdir, capsys):
    repo_path = test.init_testing_repo(APKG_BASE_DIR, str(tmpdir))
    repo_dir = str(repo_path)
    assert repo_dir.endswith('apkg')
    with cd(repo_dir):
        assert apkg('build') == 0
    out, _ = capsys.readouterr()
    # at least one package should be printed
    assert re.match(r"pkg/pkgs/\S+/apkg\S+", out)


def test_apkg_cache(tmpdir, caplog):
    repo_path = test.init_testing_repo(APKG_BASE_DIR, str(tmpdir))
    with cd(repo_path):
        cache_path = Path('pkg/.cache.json')
        if cache_path.exists():
            os.remove(str(cache_path))

        # 1) run with --no-cache shouldn't create cache
        assert apkg('make-archive', '--no-cache') == 0
        assert not cache_path.exists()
        # 2) normal run should create cache
        assert apkg('make-archive') == 0
        assert cache_path.exists()
        # 3) should reuse archive from previous run
        assert apkg('make-archive') == 0
        # 4) --no-cache shouldn't reuse cached archive
        assert apkg('make-archive', '--no-cache') == 0

        # helpers to parse cumulative log output
        def is_relevant(r):
            if 'made archive' in r.message:
                return True
            if 'reuse cached archive' in r.message:
                return True
            return False

        def msg_head(r):
            head, _, _ = r.message.partition(' ')
            return head

        # pick relevant log lines's heads
        msgs = [msg_head(r) for r in caplog.records if is_relevant(r)]

        # make sure cached archive was reused only when it should
        assert msgs == [
            'made',  # 1) should create archive
            'made',  # 2) should create archive as 2) didn't cache it
            'reuse',  # 3) should reuse archive from 2)
            'made',  # 4) should create archive due to --no-cache
            ]
