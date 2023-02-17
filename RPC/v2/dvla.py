from flask import current_app as rpc

from RPC.helper.decorators import require_token
from RPC.models import DVLAVehicle, RPCGrantType
from RPC.roots import Api

routes = Api()


@routes.get("/lookup/<string:reg>")
@require_token(RPCGrantType.DVLALookup)
def reg_lookup(reg: str):
    result = rpc.providers["dvla"].lookup(reg)
    return (
        result.str_basic,
        200,
    )


@routes.get("/lookup_inline/<string:reg>")
def reg_lookup_inline(reg: str):
    result = rpc.providers["dvla"].lookup(reg)
    if isinstance(result, DVLAVehicle):
        return (result.str_full, 200)
    return result, 404
