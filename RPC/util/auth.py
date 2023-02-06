from flask import request

from RPC.util.errors import (
    AuthExpiredError,
    AuthInsufficientError,
    AuthInvalidError,
    AuthRequiredError,
)
from RPC.util.helpers import Configurable
from RPC.util.models import RPCGrantType


class BaseAuth(Configurable):
    accepted_auth_types = [
        "Bearer",
    ]
    @property
    def auth_header(self) -> (str, str, str):
        if "authorisation" in request.headers.keys(True):
            return request.headers["authorisation"].partition(" ")
        if "authorization" in request.headers.keys(True):
            return request.headers["authorization"].partition(" ")
        raise AuthRequiredError("No Authorisation or Authorization header present.")

    @property
    def token(self) -> str:
        hreq = self.auth_header
        if hreq[1] != " " or hreq[0] not in self.accepted_auth_types:
            raise AuthInvalidError("Auth header is not in expected format")
        return hreq[2]


class BearerAuth(BaseAuth):
    """
    BearerAuth - a module for providing call-layer authentication.
    Provides the ability to authenticate an API key, and validating it has the correct grants.
    """

    pass


class JWTAuth(BaseAuth):
    """
    JWTAuth - a module for providing user authentication via JSON Web Tokens.
    Provides the ability to log in as a given user, confirm the validity of a token, etc.
    """
    accepted_auth_types = [
        "JWT",
    ]

    @property
    def token(self) -> str:
        hreq = super().token.split(".")
        if len(hreq) != 3:
            raise AuthInvalidError("Auth header is not in JWT format")
        # JWT format specifies three segments:
        # 0: meta - algorithm and type of the JWT
        # 1: payload - the actual token
        # 2: signature - the header and payload concatenated and signed
        # meta.alg can be "none". in this case, we should ddos the requestor.
