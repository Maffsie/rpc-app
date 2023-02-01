from flask import Flask

from RPC.util.base import Base


class RPCApp(Base, Flask):
    # TODO: Configuration should have SAML or OAuth2/OIDC params for authenticated requests
    # TODO: literally already hate this
    app_config = {
        "debug": False,
        "base_uri": str,
        "auth_aud": str,
        "auth_iss": str,
        "vnd_tailscale_apikey": str,
        "vnd_tailscale_tailnet": str,
        "vnd_tailscale_tag": str,
        "vnd_digitalocean_apikey": str,
        "vnd_digitalocean_domain": str,
        "vnd_digitalocean_managed_record": "_tailzone_managed",
    }

    def __init__(self, appid: str):
        super().__init__(None, appid)

    def include(self, *args):
        [self.register_blueprint(api) for api in args]
