from enum import Enum
from typing import Union
from uuid import UUID
from uuid import uuid1 as uuid

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


class Logger:
    _debug: bool = False

    def __init__(self, correlation_id: Union[UUID, None] = None, debug: bool = False):
        self.cid = correlation_id if correlation_id is not None else uuid()
        self._debug = debug

    def write(self, level: LogLevel, msg: str, *args, **kwargs):
        """
        Simple logger function. Prints a correlation ID, the log level and the message.
        If any extra arguments are passed, they're printed separately with a correlation ID derived
        from the main correlation ID.
        """
        if not isinstance(level, LogLevel):
            level = coerce_type(level, LogLevel)
        if level == LogLevel.DEBUG and not self._debug:
            return
        this_cid = uuid(self.cid.node)
        print(f"{self.cid} {level.name}: {msg}")
        if args:
            print(f"{self.cid} -> {this_cid} args: {args}")
        if kwargs:
            print(f"{self.cid} -> {this_cid} kwargs: {kwargs}")

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
