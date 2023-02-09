from flask import Flask

from RPC.util.base import Base


class RPCApp(Base, Flask):
    app_config = {
        "debug": False,
        "base_uri": str,
    }
    providers = {}
    services = {}

    def __init__(self, appid: str):
        super().__init__(None, appid)
        self.setup_providers()
        self.setup_services()

    def include(self, *args):
        [self.register_blueprint(api) for api in args]

    def setup_providers(self):
        # TODO: this should really be dynamic..
        from RPC.vnd.dvla import Doovla
        from RPC.vnd.switchbot import Switchbot

        self.providers["dvla"] = Doovla()
        self.providers["switchbot"] = Switchbot()

    def setup_services(self):
        # TODO: dynamic loader for services
        pass
