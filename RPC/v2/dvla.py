from flask import current_app as rpc

from RPC.util.base import Api
from RPC.util.decorators import require_token
from RPC.util.models import RPCGrantType, DVLAVehicle

routes = Api()


@routes.route("/lookup/<string:reg>")
@require_token(RPCGrantType.DVLALookup)
def reg_lookup(reg: str):
    result = rpc.providers["dvla"].lookup(reg)
    return (
        result.str_basic,
        200,
    )


@routes.route("/lookup_inline/<string:reg>")
def reg_lookup_inline(reg: str):
    result = rpc.providers["dvla"].lookup(reg)
    if isinstance(result, DVLAVehicle):
        return (
            result.str_full,
            200
        )
    return result, 404
