import logging

from apkg import terminal


ERROR = logging.ERROR
WARN = logging.WARN
INFO = logging.INFO
# between info and debug
VERBOSE = int((logging.INFO + logging.DEBUG) / 2)
DEBUG = logging.DEBUG

logging.basicConfig(format='%(message)s', level=INFO)
# global log instance
log = logging.getLogger()


class LogTerminal(terminal.Terminal):
    @property
    def warn(self):
        return self.yellow

    @property
    def important(self):
        return self.yellow_bold

    @property
    def error(self):
        return self.red

    @property
    def good(self):
        return self.green

    @property
    def command(self):
        return self.cyan

    @property
    def sudo(self):
        return self.magenta



# global terminal instance for color printing
T = LogTerminal()


def set_colors(colors):
    global T
    if colors == 'yes':
        if not terminal.COLOR_TERMINAL:
            return False
        T = LogTerminal(force_styling=True)
        return True
    elif colors == 'no':
        if not terminal.COLOR_TERMINAL:
            return True
        T = LogTerminal(force_styling=None)
        return True
    elif colors == 'auto':
        T = LogTerminal()
        return True
    return False


def error(*args, **kwargs):
    if args:
        msg, *rest = args
        args = [T.error('E %s' % msg)] + rest
    log.error(*args, **kwargs)


def warn(*args, **kwargs):
    if args:
        msg, *rest = args
        args = [T.warn('W %s' % msg)] + rest
    log.warning(*args, **kwargs)


def success(*args, **kwargs):
    if args:
        msg, *rest = args
        # NOTE: change prefix to S if ✓ proves to be troublesome
        #       but I thought we're in 2020+ with unicode support ¯\_(ツ)_/¯
        args = [T.good('✓ %s' % msg)] + rest
    log.info(*args, **kwargs)


def bold(*args, **kwargs):
    if args:
        msg, *rest = args
        args = [T.bold('I %s' % msg)] + rest
    log.info(*args, **kwargs)


def info(*args, **kwargs):
    if args:
        msg, *rest = args
        args = ['I %s' % msg] + rest
    log.info(*args, **kwargs)


def verbose(*args, **kwargs):
    if args:
        msg, *rest = args
        args = ['V %s' % msg] + rest
    log.log(VERBOSE, *args, **kwargs)


def debug(*args, **kwargs):
    if args:
        msg, *rest = args
        args = ['D %s' % msg] + rest
    log.debug(*args, **kwargs)


def command(*args, **kwargs):
    if args:
        msg, *rest = args
        args = [T.command('$ %s' % msg)] + rest
    log.info(*args, **kwargs)


def sudo(*args, **kwargs):
    if args:
        msg, *rest = args
        args = [T.sudo('# %s' % msg)] + rest
    log.info(*args, **kwargs)
