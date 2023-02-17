from importlib import import_module
from pkgutil import iter_modules

from flask import Flask

from .roots import Base


class RPCApp(Base, Flask):
    app_config = {
        "debug": False,
        "base_uri": str,
    }
    providers = {}
    services = {}

    def __init__(self, appid: str):
        super().__init__(None, appid)
        # Override the Flask logger
        self.logger = self.log.get_logger(__name__)
        self.setup_providers()
        self.setup_services()
        self.find_routes()

    def find_routes(self):
        _routes = [
            getattr(import_module(name), "api")
            for _, name, _ in iter_modules([self.root_path], "RPC.")
            if name.startswith("RPC.v")
        ]
        [self.register_blueprint(api) for api in _routes]

    def setup_providers(self):
        # TODO: this should really be dynamic..
        from RPC.provider.dvla import Doovla
        from RPC.provider.switchbot import Switchbot

        self.providers["dvla"] = Doovla()
        self.providers["switchbot"] = Switchbot()

    def setup_services(self):
        # TODO: dynamic loader for services
        pass
