from flask import current_app as rpc
from flask import request

from RPC.helper.decorators import require_token
from RPC.models import DVLAError, DVLAVehicle, RPCGrantType
from RPC.roots import Api, RPCRequest

routes = Api()
request: RPCRequest


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
    request.log.info("dvla ves lookup", step="begin", registration=reg)
    result = rpc.providers["dvla"].lookup(reg)
    request.log.info(
        "dvla ves lookup",
        step="end",
        registration=reg,
        success=isinstance(result, DVLAVehicle),
    )
    if isinstance(result, DVLAVehicle):
        return result.str_full, 200
    if isinstance(result, DVLAError):
        return result.as_view(), result.major
    return result, 404
