"""
  ehandler

  well-behaved exception handler for python cli commands

"""

import sys
from traceback import format_exception


def exception_handler(
    exception_type,
    exception,
    traceback,
    debug_hook=sys.excepthook,
):
    logger = ExceptionHandler.logger

    elist = format_exception(exception)
    traceback_msg = "".join(elist[:-1]).rstrip("\n")
    error_msg = elist[-1].rstrip("\n")

    if logger:
        logger.debug(traceback_msg)
        logger.error(error_msg)

    if ExceptionHandler.debug:

        debug_hook(
            exception_type,
            exception,
            traceback,
        )

    elif not logger:
        print(error_msg, file=sys.stderr, end="\n", flush=True)

    sys.exit(-1)


class ExceptionHandler:

    installed = False
    debug = None
    logger = None

    def __init__(self, debug=False, logger=False):
        self.__class__.debug = debug
        self.__class__.logger = logger
        if not self.installed:
            sys.excepthook = exception_handler
            self.__class__.installed = True
