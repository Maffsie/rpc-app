from RPC.util import Base


class RPCApp(Base):
    # TODO: Configuration should have SAML or OAuth2/OIDC params for authenticated requests
    config = {
        "debug": False,
        "base_uri": str,
    }
