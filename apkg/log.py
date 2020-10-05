import logging

from apkg import terminal


WARN = logging.WARN
INFO = logging.INFO
# between info and debug
VERBOSE = (logging.INFO + logging.DEBUG) / 2
DEBUG = logging.DEBUG

logging.basicConfig(format='%(message)s', level=logging.INFO)
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
    def cmd(self):
        return self.cyan


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
        largs = list(args)
        largs[0] = T.error(args[0])
        args = tuple(largs)
    log.error(*args, **kwargs)


def warn(*args, **kwargs):
    if args:
        largs = list(args)
        largs[0] = T.warn(args[0])
        args = tuple(largs)
    log.warning(*args, **kwargs)


def success(*args, **kwargs):
    if args:
        largs = list(args)
        largs[0] = T.good(args[0])
        args = tuple(largs)
    log.info(*args, **kwargs)


def info(*args, **kwargs):
    log.info(*args, **kwargs)


def verbose(*args, **kwargs):
    log.log(VERBOSE, *args, **kwargs)


def debug(*args, **kwargs):
    log.debug(*args, **kwargs)


def command(*args, **kwargs):
    log.info(*args, **kwargs)
