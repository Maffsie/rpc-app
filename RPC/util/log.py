import logging
from enum import Enum
from typing import Union
from uuid import UUID
from uuid import uuid1 as uuid

from logging_loki import LokiHandler

from RPC.util.coercion import coerce_type
from RPC.helper import Configurable


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
            self.app_config["debug"] = debug
        self._logger = logging.getLogger(str(self.cid))
        self._logger.setLevel("DEBUG" if self.app_config.get("debug") else "INFO")
        self._logger.addHandler(
            LokiHandler(
                url=self.app_config.get("loki_url"),
                tags={
                    "app": "RPC",
                },
                version="1",
            )
        )
        # logging.captureWarnings(True)

    def get_logger(self, name: str) -> logging.Logger:
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

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(
            msg,
            extra={
                "tags": {
                    "correlation_id": str(self.cid),
                },
                "extra_args": [
                    *args,
                ],
                "extra_kwargs": {
                    **kwargs,
                },
            },
        )

    def verbose(self, msg, *args, **kwargs):
        self._logger.log(
            15,
            msg,
            extra={
                "tags": {
                    "correlation_id": str(self.cid),
                },
                "extra_args": [
                    *args,
                ],
                "extra_kwargs": {
                    **kwargs,
                },
            },
        )

    def info(self, msg, *args, **kwargs):
        self._logger.info(
            msg,
            extra={
                "tags": {
                    "correlation_id": str(self.cid),
                },
                "extra_args": [
                    *args,
                ],
                "extra_kwargs": {
                    **kwargs,
                },
            },
        )

    def notice(self, msg, *args, **kwargs):
        self._logger.log(
            25,
            msg,
            extra={
                "tags": {
                    "correlation_id": str(self.cid),
                },
                "extra_args": [
                    *args,
                ],
                "extra_kwargs": {
                    **kwargs,
                },
            },
        )

    def warn(self, msg, *args, **kwargs):
        self._logger.warning(
            msg,
            extra={
                "tags": {
                    "correlation_id": str(self.cid),
                },
                "extra_args": [
                    *args,
                ],
                "extra_kwargs": {
                    **kwargs,
                },
            },
        )

    def error(self, msg, *args, **kwargs):
        self._logger.error(
            msg,
            extra={
                "tags": {
                    "correlation_id": str(self.cid),
                },
                "extra_args": [
                    *args,
                ],
                "extra_kwargs": {
                    **kwargs,
                },
            },
        )

    def fatal(self, msg, *args, **kwargs):
        self._logger.critical(
            msg,
            extra={
                "tags": {
                    "correlation_id": str(self.cid),
                },
                "extra_args": [
                    *args,
                ],
                "extra_kwargs": {
                    **kwargs,
                },
            },
        )
