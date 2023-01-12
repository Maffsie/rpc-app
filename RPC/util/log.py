from enum import Enum
from uuid import UUID
from uuid import uuid1 as uuid


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


class Logger:
    def __init__(self, correlation_id: UUID = None):
        self.cid = correlation_id if correlation_id is not None else uuid()

    def write(self, level: LogLevel, msg: str, *args, **kwargs):
        """
        Simple logger function. Prints a correlation ID, the log level and the message.
        If any extra arguments are passed, they're printed separately with a correlation ID derived
        from the main correlation ID.
        """
        if not isinstance(level, LogLevel):
            level = self.coerce_type(level, LogLevel)
        if level == LogLevel.DEBUG and not self.config["debug"]:
            return
        this_cid = uuid(self.cid.node)
        print(f"{self.cid} {level.name}: {msg}")
        if args:
            print(f"{self.cid} -> {this_cid} args: {args}")
        if kwargs:
            print(f"{self.cid} -> {this_cid} kwargs: {kwargs}")
