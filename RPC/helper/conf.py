from os import environ, listdir
from pathlib import Path
from warnings import warn

from dotenv import load_dotenv

from RPC.util.coercion import coerce_type
from RPC.util.errors import RPCInitialisationException

from .decorators import coerce_args

search_files = ["/env", "/.env", "./env", "./.env"]
search_paths = [
    "/configs",
    "/run/configs",
    "/run/secrets",
    "/secrets",
    "/var/run/configs",
    "/var/run/secrets",
]


def preconfigure(conf_file=search_files, conf_paths=search_paths):
    @coerce_args([(0, Path)])
    def _preconf_one(path: Path):
        if not path.exists():
            return
        if not path.is_dir():
            return load_dotenv(dotenv_path=path.resolve())
        for file in listdir(path.resolve()):
            load_dotenv(dotenv_path=file)

    if coerce_type(environ.get("NO_CONF_FILES", False), bool):
        return
    _ = [_preconf_one(path) for path in [*conf_file, *conf_paths]]

    if len([*conf_file, *conf_paths]) == 0:
        raise RPCInitialisationException(
            "No config files could be found! Please supply some, "
            "or set environment variable NO_CONF_FILES=True"
        )
    # No need to error-check this, dotenv handles it fine
    [load_dotenv(dotenv_path=fp) for fp in conf_file]
    # Need to error-check this
    for path in conf_paths:
        try:
            [
                load_dotenv(dotenv_path=f"{path}/{filename}")
                for filename in listdir(path)
            ]
        except FileNotFoundError:
            pass


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
        value = coerce_type(
            environ.get(name.upper(), environ.get(name, default)), deftype
        )
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
    return conf


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
        self._load_conf()
        super().__init__(*args, **kwargs)

    def _load_conf(self):
        self.app_config = load_conf_static(self.app_config, self.errnos, self.errdes)
