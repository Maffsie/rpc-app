from flask import Flask

from RPC.util.base import Base


class RPCApp(Base, Flask):
    # TODO: Configuration should have SAML or OAuth2/OIDC params for authenticated requests
    app_config = {
        "debug": False,
        "base_uri": str,
        "vnd_tailscale_apikey": str,
        "vnd_tailscale_tailnet": str,
        "vnd_tailscale_tag": str,
        "vnd_digitalocean_apikey": str,
        "vnd_digitalocean_domain": str,
        "vnd_digitalocean_managed_record": "_tailzone_managed",
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
        self.providers["dvla"] = Doovla()

    def setup_services(self):
        # TODO: dynamic loader for services
        pass
