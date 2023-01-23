import inspect
from os import environ as env
from typing import Union
from uuid import UUID

from flask import Blueprint

from .coercion import coerce_type
from .conf import preconfigure
from .log import Logger, LogLevel


class Base:
    app_config = {
        "debug": False,
    }
    errnos = {
        "debug": "NDEBUGSET",
    }
    errdes = {
        "NDEBUGSET": "Debug logging is enabled.",
    }
    init = 0

    def __init__(self, correlation_id: Union[UUID, None] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init = 1
        self.log = Logger(correlation_id=correlation_id)
        preconfigure()
        self.load_conf()
        self.log._debug = self.app_config.get("debug")
        self.init = 2

    def load_conf(self):
        """
        Load all configuration values from the execution environment if possible
        """

        def load_conf_one(name, default=None):
            """
            Load the given configuration value from the execution environment if possible.
            If the value is not present, and a default has been set for that parameter, use that.
            If the value is not present and an errno is set for its absence, log that.
            """
            deftype = default
            if not isinstance(deftype, type):
                deftype = type(deftype)
            value = coerce_type(env.get(name, default), deftype)
            self.log.write(
                LogLevel.DEBUG,
                f"env ${name}? {type(value)} '{value}' : {deftype} '{default}'",
            )
            err = self.errnos.get(name, None)
            if err is not None and value is None:
                self.log.write(
                    LogLevel[err[0]],
                    f"{err} ¦ {self.errdes.get(err, 'no descriptor for this errno')}",
                )
                match err[0]:
                    case "E":
                        raise Exception(err)
            return value

        for entry in self.app_config:
            self.app_config[entry] = load_conf_one(
                entry.upper(), self.app_config[entry]
            )


class Micro:
    conf = {}
    log: Logger = None

    def __init__(
        self,
        conf: dict,
        correlation_id: Union[UUID, None] = None,
        logger: Logger = None,
        *args,
        **kwargs,
    ):
        self.conf = conf
        if logger is not None:
            self.log = logger
        else:
            self.log = Logger(correlation_id=correlation_id)
            self.log._debug = self.conf.get("debug")
        self.__subinit__(*args, **kwargs)

    # stub
    def __subinit__(self, *args, **kwargs):
        pass


class Api(Blueprint):
    def __init__(self, *args, url_prefix: str = None, **kwargs):
        stack = inspect.stack()
        caller = stack[1].function
        callermod = inspect.getmodule(stack[1]).__name__
        if caller in ("<module>", "__init__"):
            caller = stack[1].filename.split(".")[0]
        if url_prefix is None or isinstance(url_prefix, str) and len(url_prefix) == 0:
            url_prefix = f"/{caller}"
        super().__init__(
            *args, name=caller, import_name=callermod, url_prefix=url_prefix, **kwargs
        )

    def include(self, *args):
        [self.register_blueprint(api) for api in args]
