from flask import request

from RPC.util.errors import (
    AuthExpiredError,
    AuthInsufficientError,
    AuthInvalidError,
    AuthRequiredError,
)
from RPC.util.helpers import Configurable
from RPC.util.models import RPCGrantType


class BearerAuth(Configurable):
    """
    BearerAuth - a module for providing call-layer authentication.
    Provides the ability to authenticate an API key, and validating it has the correct grants.
    """

    app_config = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check(self, with_grant: RPCGrantType | None = None):
        if ("authorization" not in request.headers.keys(True)
            and "authorisation" not in request.headers.keys(True)
        ):
            raise AuthRequiredError("No Authorisation or Authorization header present.")



class JWTAuth(Configurable):
    """
    JWTAuth - a module for providing user authentication via JSON Web Tokens.
    Provides the ability to log in as a given user, confirm the validity of a token, etc.
    """

    pass
