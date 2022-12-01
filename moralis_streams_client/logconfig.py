# logging configuration

import logging
import sys

from . import settings


def configure_logging(log_level=None, log_file=None, log_format=None):

    log_level = log_level or settings.LOG_LEVEL
    log_file = log_file or settings.LOG_FILE
    log_format = log_format or settings.LOG_FORMAT

    args = dict(force=True, level=log_level, format=log_format)
    if log_file:
        args["filename"] = str(log_file)
    else:
        args["stream"] = sys.stderr

    logging.basicConfig(**args)

    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
