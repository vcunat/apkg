# -*- encoding: utf-8 -*-
import six
import subprocess

from apkg import exception
from apkg import log


def log_cmd_fail(cmd, cout, fail_log_fun=log.warn, out_log_fun=log.info):
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


def run(cmd, *params, **kwargs):
    fatal = kwargs.get('fatal', True)
    direct = kwargs.get('direct', False)
    log_cmd = kwargs.get('log_cmd', True)
    log_fail = kwargs.get('log_fail', True)
    input = kwargs.get('input')
    print_stdout = kwargs.get('print_stdout', False)
    print_stderr = kwargs.get('print_stderr', False)
    print_output = kwargs.get('print_output', False)
    env = kwargs.get('env', None)

    cmd = [cmd]
    cmd.extend(p if isinstance(p, six.string_types) else six.text_type(p)
               for p in params)
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

    if out:
        out = out.rstrip()
        if print_stdout:
            log.info(out)
    else:
        out = b''

    if err:
        err = err.rstrip()
        if print_stderr:
            log.info(err)
    else:
        err = b''

    cout = _CommandOutput(out.decode('utf-8'))
    cout.stderr = err
    cout.return_code = prc.returncode
    cout.cmd = cmd_str
    if prc.returncode != 0:
        if log_fail:
            log_cmd_fail(cmd_str, cout)
        if fatal:
            raise exception.CommandFailed(cmd=cmd, out=cout)
    return cout


class _CommandOutput(str):
    """
    Just a string subclass with attribute access.
    """
    @property
    def success(self):
        return self.return_code == 0


class ShellCommand(object):
    command = None

    def __init__(self):
        if self.command is None:
            self.command = self.__class__.__name__.lower()

    def __call__(self, *params, **kwargs):
        return run(self.command, *params, **kwargs)
