class ApkgException(Exception):
    msg_fmt = "An unknown error occurred"
    exit_code = 1

    def __init__(self, msg=None, exit_code=None, **kwargs):
        self.kwargs = kwargs
        if not msg:
            try:
                msg = self.msg_fmt % kwargs
            except Exception:
                # kwargs doesn't match those in message.
                # Returning this is still better than nothing.
                msg = self.msg_fmt
        if exit_code is not None:
            self.exit_code = exit_code
        super(ApkgException, self).__init__(msg)


class InvalidType(ApkgException):
    msg_fmt = "Invalid type: $(var) must be %(desired)s but is %(type)s"
    exit_code = 14


class InvalidChoice(ApkgException):
    msg_fmt = "Invalid choice: %(var)s must be one of: %(opts)s (is: %(val)s)"
    exit_code = 16


class InvalidFormat(ApkgException):
    msg_fmt = "Invalid format: %(fmt)s"
    exit_code = 18


class HTTPRequestFailed(ApkgException):
    msg_fmt = "HTTP request failed with code %(code)s: %(request)s"
    exit_code = 44


class CommandNotFound(ApkgException):
    msg_fmt = "Command not found: %(cmd)s"
    exit_code = 60


class CommandFailed(ApkgException):
    msg_fmt = "Command failed: %(cmd)s"
    exit_code = 62
