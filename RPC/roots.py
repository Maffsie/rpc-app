import inspect
from importlib import import_module
from logging import getLogger
from pkgutil import iter_modules
from uuid import UUID

from flask import Blueprint, Request
from requests import Session

from RPC.helper import Configurable
from RPC.util.log import Logger


class Base(Configurable):
    def __init__(self, correlation_id: UUID | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = Logger(correlation_id=correlation_id)


class RPCRequest(Request):
    log: Logger

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        calling_frame = inspect.stack()[1]
        callermod = calling_frame.frame.f_locals.get(
            "__name__", type(calling_frame.frame.f_locals["self"]).__module__
        )
        self.log = Logger(context=callermod)


class Micro:
    conf = {}
    log: Logger = None

    def __init__(
        self,
        conf: dict,
        correlation_id: UUID | None = None,
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
    log = None

    def __init__(
        self, *args, url_prefix: str | None = None, auto: bool = False, **kwargs
    ):
        """
        Subclass of `flask.Blueprint` with some QoL enhancements for automatic inferrence
        of name, import name, url prefix and automatic loading of child modules

        :param auto: if True, loads routes from all immediate child modules
        :type auto: bool
        :param url_prefix: if specified, overrides automatic inferrence of url prefix
        :type url_prefix: str | None
        """
        # this is absolutely hideous
        # but there's not really an obvious way to more cleanly get the caller's name
        # and package without doing introspection like this.
        # the upshot is, however, that instead of
        # Blueprint(name="myapi", import_name=__name__, url_prefix="/myapi")
        # it's just.. Api()
        # which resolves to Blueprint(name="myapi", import_name="MyPackage.myapi", ...)
        calling_frame = inspect.stack()[1]
        caller = calling_frame.function
        callermod = calling_frame.frame.f_locals["__name__"]
        if caller == "<module>":
            caller = calling_frame.filename.split("/")[-1].partition(".")[0]
        if caller == "__init__":
            caller = calling_frame.frame.f_locals["__package__"].split(".")[-1]
        if url_prefix is None or (isinstance(url_prefix, str) and len(url_prefix) == 0):
            url_prefix = f"/{caller}"
        self.log = Logger()
        super().__init__(
            *args, name=caller, import_name=callermod, url_prefix=url_prefix, **kwargs
        )
        if auto:
            self.find_routes()

    def register_blueprint(self, blueprint, *args, **kwargs):
        self.log.info(
            f"Registering routes from {blueprint.name} on sub-prefix {blueprint.url_prefix}"
        )
        super().register_blueprint(blueprint, *args, **kwargs)

    def find_routes(self):
        """
        Searches for modules below the current module and registers their blueprints, if any
        """
        [
            self.register_blueprint(getattr(route, "routes"))
            for route in [
                import_module(name)
                for _, name, _ in iter_modules([self.root_path], self.import_name + ".")
                if name != self.import_name
                and name.startswith(self.import_name.rpartition(".")[0] + ".")
            ]
            if hasattr(route, "routes") and not hasattr(route, "_no_auto")
        ]


class IApi(Session):
    """
    Base class for API implementations.
    Expects the `baseurl` string to be overridden.
    Expects all requests to be relative to the `baseurl`.
    """

    baseurl: str = None

    # needed to ensure chainability
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def request(self, method, url, *args, **kwargs):
        return super().request(
            method=method, url=f"{self.baseurl}/{url}", *args, **kwargs
        )
