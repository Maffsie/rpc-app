import inspect
from uuid import UUID

from flask import Blueprint

from RPC.util.helpers import Configurable
from RPC.util.log import Logger


class Base(Configurable):
    def __init__(self, correlation_id: UUID | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = Logger(correlation_id=correlation_id)


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
    def __init__(self, *args, url_prefix: str = None, **kwargs):
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
        super().__init__(
            *args, name=caller, import_name=callermod, url_prefix=url_prefix, **kwargs
        )

    def include(self, *args):
        [self.register_blueprint(api) for api in args]
