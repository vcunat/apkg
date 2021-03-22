from pathlib import Path
import sys

from apkg import ex
from apkg.log import getLogger
import apkg.util.shutil35 as shutil


log = getLogger(__name__)


def copy_paths(paths, dst):
    """
    utility to copy a list of paths to dst
    """
    if not dst.exists():
        dst.mkdir(parents=True, exist_ok=True)
    dst_full = dst.resolve()
    new_paths = []
    for p in paths:
        if p.parent.resolve() == dst_full:
            new_paths.append(p)
        else:
            p_dst = dst / p.name
            log.verbose("copying file: %s -> %s", p, p_dst)
            shutil.copy(p, p_dst)
            new_paths.append(p_dst)
    return new_paths


def get_cached_paths(proj, cache_name, cache_key,
                     result_dir=None):
    """
    get cached files and move them to result_dir if specified
    """
    paths = proj.cache.get(cache_name, cache_key)
    if not paths:
        return None
    if result_dir:
        paths = copy_paths(paths, Path(result_dir))
    return paths


def print_results(results):
    """
    print results received from apkg command
    """
    try:
        for r in results:
            print(str(r))
    except TypeError:
        print(str(results))


def parse_input_files(files, file_lists):
    """
    utility to parse apkg input files and input file lists
    into a single list of input files
    """
    all_files = [Path(f) for f in files]

    if len([fl for fl in file_lists if fl == '-']) > 1:
        fail = "requested to read stdin multiple times"
        raise ex.InvalidInput(fail=fail)

    for fl in file_lists:
        if fl == '-':
            f = sys.stdin
        else:
            f = open(fl, 'r')
        all_files += [Path(ln.strip()) for ln in f.readlines()]
        f.close()

    return all_files


def ensure_input_files(infiles):
    if not infiles:
        raise ex.InvalidInput(
            fail="no input file(s) specified")
    for f in infiles:
        if not f.exists():
            raise ex.InvalidInput(
                fail="input file not found: %s" % f)
