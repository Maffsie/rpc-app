from flask import Flask

from RPC.util import Base


class RPCApp(Base, Flask):
    # TODO: Configuration should have SAML or OAuth2/OIDC params for authenticated requests
    app_config = {
        "debug": False,
        "base_uri": str,
        "auth_aud": str,
        "auth_iss": str,
    }

    def __init__(self, appid: str):
        super().__init__(None, appid)
