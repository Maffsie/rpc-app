from flask import current_app

from RPC.util.base import Api
from RPC.util.decorators import require_token
from RPC.util.models import RPCGrantType

routes = Api()


@routes.route("/lookup/<string:reg>")
@require_token(RPCGrantType.DVLALookup)
def reg_lookup(reg: str):
    result = current_app.providers["dvla"].lookup(reg)
    return (
        result.str_basic,
        200,
    )


@routes.route("/lookup_inline/<string:reg>")
def reg_lookup_inline(reg: str):
    result = current_app.providers["dvla"].lookup(reg)
    return (
        result.str_basic,
        200
    )
