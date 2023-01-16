from os import environ as env
from typing import Union
from uuid import UUID

from .coercion import coerce_type
from .conf import preconfigure
from .log import Logger, LogLevel


class Base:
    config = {
        "debug": False,
    }
    errnos = {
        "debug": "NDEBUGSET",
    }
    errdes = {
        "NDEBUGSET": "Debug logging is enabled.",
    }

    def __init__(self, correlation_id: Union[UUID, None] = None):
        self.log = Logger(correlation_id=correlation_id)
        preconfigure()
        self.load_conf()

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
            value = coerce_type(env.get(name, default), type(default))
            self.log.write(
                LogLevel.DEBUG,
                f"env ${name}? {type(value)} '{value}' : {type(default)} '{default}'",
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

        for entry in self.config:
            self.config[entry] = load_conf_one(entry.upper(), self.config[entry])
