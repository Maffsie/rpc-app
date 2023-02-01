from os import environ as env
from warnings import warn

from .coercion import coerce_type
from .conf import preconfigure


def load_conf_static(conf, errno, errdesc):
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
        if isinstance(deftype, type):
            default = None
        value = coerce_type(env.get(name.upper(), env.get(name, default)), deftype)
        # warn(f"env ${name}? {type(value)} '{value}' : {deftype} '{default}'")
        err = errno.get(name, None)
        err_d = errdesc.get(err, "no descriptor for this errno")
        if err is not None and value is None:
            warn(f"{err} ¦ {err_d}")
            match err[0]:
                case "E" | "F":
                    raise Exception(err, err_d)
        return value

    for entry in conf:
        conf[entry] = load_conf_one(entry, conf[entry])


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

    def __init__(self, *args, **kwargs):
        preconfigure()
        self.load_conf()
        super().__init__(*args, **kwargs)

    def load_conf(self):
        self.app_config = load_conf_static(self.app_config, self.errnos, self.errdes)
