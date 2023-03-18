from flask import current_app as rpc
from flask import request

from RPC.helper.decorators import require_token
from RPC.models import DVSAVehicle, RPCGrantType
from RPC.roots import Api, RPCRequest

routes = Api()
request: RPCRequest


@routes.get("/lookup/<string:reg>")
@require_token(RPCGrantType.DVSALookup)
def reg_lookup(reg: str):
    result = rpc.providers["dvsa"].lookup(reg)
    return (
        result.str_basic,
        200,
    )


@routes.get("/lookup_inline/<string:reg>")
def reg_lookup_inline(reg: str):
    request.log.info("dvsa ves lookup", step="begin", registration=reg)
    result = rpc.providers["dvsa"].lookup_single(reg)
    request.log.info(
        "dvla ves lookup",
        step="end",
        registration=reg,
        success=isinstance(result, DVSAVehicle),
    )
    if isinstance(result, DVSAVehicle):
        return result.str_full, 200
    return result, 404