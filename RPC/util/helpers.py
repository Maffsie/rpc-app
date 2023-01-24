from os import environ as env
from warnings import warn

from .coercion import coerce_type
from .conf import preconfigure


class Configurable:
    app_config = {
        "debug": False,
    }
    errnos = {
        "debug": "NDEBUGSET",
    }
    errdes = {
        "NDEBUGSET": "Debug logging is enabled.",
    }

    def __init__(self):
        preconfigure()

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
            # warn(f"env ${name}? {type(value)} '{value}' : {deftype} '{default}'")
            err = self.errnos.get(name, None)
            if err is not None and value is None:
                warn(f"{err} ¦ {self.errdes.get(err, 'no descriptor for this errno')}")
                match err[0]:
                    case "E":
                        raise Exception(err)
            return value

        for entry in self.app_config:
            self.app_config[entry] = load_conf_one(
                entry.upper(), self.app_config[entry]
            )
