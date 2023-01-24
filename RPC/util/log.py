import logging
from enum import Enum
from typing import Union
from uuid import UUID
from uuid import uuid1 as uuid

from pygelf import GelfHttpsHandler

from .base import Micro
from .coercion import coerce_type


class LogLevel(Enum):
    DEBUG = 0
    D = 0
    VERBOSE = 1
    V = 1
    INFO = 2
    I = 2
    NOTICE = 3
    N = 3
    WARNING = 4
    WARN = 4
    W = 4
    ERROR = 5
    ERR = 5
    E = 5
    YOUHAVEFUCKEDUP = 6
    FATAL = 6
    F = 6


class Logger(Micro):
    _logger = None

    conf = {
        "debug": False,
        "gelf_host": str,
        "gelf_port": 443,
        "gelf_tls_validate": False,
    }

    def __init__(
        self,
        *args,
        correlation_id: Union[UUID, None] = None,
        debug: bool = False,
        **kwargs,
    ):
        self.cid = correlation_id if correlation_id is not None else uuid()
        super().__init__(*args, **kwargs)
        if debug:
            self.conf["debug"] = debug
        self._logger = logging.getLogger()
        self._logger.addHandler(
            GelfHttpsHandler(
                host=self.conf.get("gelf_host"),
                port=self.conf.get("gelf_port"),
                validate=self.conf.get("gelf_tls_validate"),
            )
        )
        logging.captureWarnings(True)

    def write(self, level: LogLevel, msg: str, *args, **kwargs):
        """
        Simple logger function. Prints a correlation ID, the log level and the message.
        If any extra arguments are passed, they're printed separately with a correlation ID derived
        from the main correlation ID.
        """
        if not isinstance(level, LogLevel):
            level = coerce_type(level, LogLevel)
        if level == LogLevel.DEBUG and not self.conf.get("debug"):
            return
        self._logger.log(
            level.value, msg, args=args, extra={"correlation_id": self.cid, **kwargs}
        )

    def debug(self, *args, **kwargs):
        return self.write(LogLevel.DEBUG, *args, **kwargs)

    def verbose(self, *args, **kwargs):
        return self.write(LogLevel.VERBOSE, *args, **kwargs)

    def notice(self, *args, **kwargs):
        return self.write(LogLevel.NOTICE, *args, **kwargs)

    def info(self, *args, **kwargs):
        return self.write(LogLevel.INFO, *args, **kwargs)

    def warn(self, *args, **kwargs):
        return self.write(LogLevel.WARN, *args, **kwargs)

    def error(self, *args, **kwargs):
        return self.write(LogLevel.ERROR, *args, **kwargs)

    def fatal(self, *args, **kwargs):
        return self.write(LogLevel.FATAL, *args, **kwargs)
