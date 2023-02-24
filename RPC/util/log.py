import inspect
import logging
from enum import Enum
from uuid import UUID
from uuid import uuid1 as uuid

from logging_loki import LokiHandler

from RPC.helper import Configurable
from RPC.util.coercion import coerce_type


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


class Logger(Configurable):
    _logger: logging.Logger = None

    app_config = {
        "debug": False,
        "loki_url": str,
        "loki_port": 443,
    }
    errnos = {
        "loki_url": "FLUUNSET",
    }
    errdes = {
        "FLUUNSET": "LOKI_URL not set! Hint: it should be <loki-host>/loki/api/v1/push",
    }

    tags: dict

    def __init__(
        self,
        *args,
        context: str | None = None,
        correlation_id: UUID | None = None,
        debug: bool = False,
        **kwargs,
    ):
        self.tags = {}
        self.cid = correlation_id if correlation_id is not None else uuid()
        super().__init__(*args, **kwargs)
        if debug:
            self.app_config["debug"] = debug

        # Set up root logger
        root_logger = logging.getLogger()
        if LokiHandler not in [type(h) for h in root_logger.handlers]:
            root_logger.setLevel("DEBUG" if self.app_config.get("debug") else "INFO")
            root_logger.addHandler(
                LokiHandler(
                    url=self.app_config.get("loki_url"),
                    tags={
                        "app": "RPC",
                        "cid": str(self.cid),
                    },
                    version="1",
                )
            )
        else:
            self.tags["sub_cid"] = str(self.cid)

        if context is not None:
            self.tags["context"] = context
        calling_frame = inspect.stack()[1]
        callermod = calling_frame.frame.f_locals.get(
            "__name__", type(calling_frame.frame.f_locals["self"]).__module__
        )
        self._logger = root_logger.getChild(callermod)
        # logging.captureWarnings(True)

    def get_logger(self, name: str | None = None) -> logging.Logger:
        if name is None:
            calling_frame = inspect.stack()[1]
            name = calling_frame.frame.f_locals.get(
                "__name__", type(calling_frame.frame.f_locals["self"]).__module__
            )
        return self._logger.getChild(name)

    def write(self, level: LogLevel, msg: str, *args, **kwargs):
        """
        Simple logger function. Prints a correlation ID, the log level and the message.
        If any extra arguments are passed, they're printed separately with a correlation ID derived
        from the main correlation ID.
        """
        if not isinstance(level, LogLevel):
            level = coerce_type(level, LogLevel)
        if level == LogLevel.DEBUG and not self.app_config.get("debug"):
            return
        print("don't use me i'm too gay")
        raise Exception("fuckin hell")

    def _extra(self, extra: dict, icontext: str | None = None) -> dict:
        extra["tags"] = self.tags
        if icontext is not None:
            extra["tags"]["inst_context"] = icontext
        extra["tags"]["extra"] = extra["extra_args"]
        extra["tags"].update(extra["extra_kwargs"])
        return extra

    def debug(self, msg, *args, icontext: str | None = None, **kwargs):
        self._logger.debug(
            msg,
            extra=self._extra(
                {
                    "extra_args": [
                        *args,
                    ],
                    "extra_kwargs": {
                        **kwargs,
                    },
                },
                icontext,
            ),
        )

    def verbose(self, msg, *args, icontext: str | None = None, **kwargs):
        self._logger.log(
            15,
            msg,
            extra=self._extra(
                {
                    "extra_args": [
                        *args,
                    ],
                    "extra_kwargs": {
                        **kwargs,
                    },
                },
                icontext,
            ),
        )

    def info(self, msg, *args, icontext: str | None = None, **kwargs):
        self._logger.info(
            msg,
            extra=self._extra(
                {
                    "extra_args": [
                        *args,
                    ],
                    "extra_kwargs": {
                        **kwargs,
                    },
                },
                icontext,
            ),
        )

    def notice(self, msg, *args, icontext: str | None = None, **kwargs):
        self._logger.log(
            25,
            msg,
            extra=self._extra(
                {
                    "extra_args": [
                        *args,
                    ],
                    "extra_kwargs": {
                        **kwargs,
                    },
                },
                icontext,
            ),
        )

    def warn(self, msg, *args, icontext: str | None = None, **kwargs):
        self._logger.warning(
            msg,
            extra=self._extra(
                {
                    "extra_args": [
                        *args,
                    ],
                    "extra_kwargs": {
                        **kwargs,
                    },
                },
                icontext,
            ),
        )

    def error(self, msg, *args, icontext: str | None = None, **kwargs):
        self._logger.error(
            msg,
            extra=self._extra(
                {
                    "extra_args": [
                        *args,
                    ],
                    "extra_kwargs": {
                        **kwargs,
                    },
                },
                icontext,
            ),
        )

    def fatal(self, msg, *args, icontext: str | None = None, **kwargs):
        self._logger.critical(
            msg,
            extra=self._extra(
                {
                    "extra_args": [
                        *args,
                    ],
                    "extra_kwargs": {
                        **kwargs,
                    },
                },
                icontext,
            ),
        )
