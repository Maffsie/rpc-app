from importlib import import_module
from pkgutil import iter_modules

from flask import Flask

from RPC.provider import get_providers

from .roots import Base, RPCRequest


class RPCApp(Base, Flask):
    app_config = {
        "debug": False,
        "base_uri": str,
    }
    providers = {}
    services = {}

    request_class = RPCRequest

    def __init__(self, appid: str):
        super().__init__(None, appid)
        # Override the Flask logger
        self.logger = self.log.get_logger(__name__)
        self.providers = get_providers()
        self.setup_services()
        self.find_routes()

    def register_blueprint(self, blueprint, *args, **kwargs):
        self.log.info(
            f"Registering base API {blueprint.name} on {blueprint.url_prefix}"
        )
        super().register_blueprint(blueprint, *args, **kwargs)

    def find_routes(self):
        [
            self.register_blueprint(getattr(api, "api"))
            for api in [
                import_module(name)
                for _, name, _ in iter_modules([self.root_path], "RPC.")
                if name.startswith("RPC.v")
            ]
            if hasattr(api, "api")
        ]

    def setup_services(self):
        # TODO: dynamic loader for services
        pass
