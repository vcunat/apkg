# -*- encoding: utf-8 -*-
from contextlib import contextmanager
import os
import subprocess

from apkg import exception
from apkg import log


def log_cmd_fail(cmd, cout, fail_log_fun=log.error, out_log_fun=log.info):
    fail_log_fun('{t.error}command failed: {t.normal}{t.cmd}{cmd}{t.normal}'
                 .format(t=log.T, cmd=cmd))
    nl = False
    if cout:
        out_log_fun(log.T.bold("stdout:"))
        out_log_fun(cout)
        nl = True
    if cout.stderr:
        out_log_fun(log.T.bold("stderr:"))
        out_log_fun(cout.stderr)
        nl = True
    if nl:
        out_log_fun('')


def run(*cmd, **kwargs):
    fatal = kwargs.get('fatal', True)
    direct = kwargs.get('direct', False)
    log_cmd = kwargs.get('log_cmd', True)
    log_fail = kwargs.get('log_fail', True)
    input = kwargs.get('input')
    print_stdout = kwargs.get('print_stdout', False)
    print_stderr = kwargs.get('print_stderr', False)
    print_output = kwargs.get('print_output', False)
    env = kwargs.get('env', None)

    # TODO: escape parameters with whitespace
    cmd = [str(c) for c in cmd]
    cmd_str = ' '.join(cmd)

    if log_cmd:
        log.command(log.T.cmd(cmd_str))

    if print_output:
        print_stdout = True
        print_stderr = True

    if input:
        stdin = subprocess.PIPE
        input = input
    else:
        stdin = None

    if direct:
        stdout = None
        stderr = None
    else:
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE

    try:
        prc = subprocess.Popen(cmd, stdin=stdin, stdout=stdout,
                               stderr=stderr, env=env)
    except OSError:
        raise exception.CommandNotFound(cmd=cmd[0])
    out, err = prc.communicate(input=input)

    if type(out) == bytes:
        out = out.decode('utf-8')
    if type(err) == bytes:
        err = err.decode('utf-8')

    if out:
        out = out.rstrip()
        if print_stdout:
            log.info(out)
    else:
        out = ''

    if err:
        err = err.rstrip()
        if print_stderr:
            log.info(err)
    else:
        err = ''

    cout = CommandOutput(out)
    cout.stderr = err
    cout.return_code = prc.returncode
    cout.cmd = cmd_str
    if prc.returncode != 0:
        if log_fail:
            log_cmd_fail(cmd_str, cout)
        if fatal:
            raise exception.CommandFailed(cmd=cmd, out=cout)
    return cout


@contextmanager
def cd(newdir):
    """
    Temporarily change current directory.
    """
    olddir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(olddir)


class ShellCommand(object):
    command = None

    def __init__(self):
        if self.command is None:
            self.command = self.__class__.__name__.lower()

    def __call__(self, *params, **kwargs):
        return run(self.command, *params, **kwargs)


class CommandOutput(str):
    """
    Just a string subclass with attribute access.
    """
    @property
    def success(self):
        return self.return_code == 0