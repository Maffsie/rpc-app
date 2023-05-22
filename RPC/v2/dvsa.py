from flask import current_app as rpc
from flask import request

from RPC.helper.decorators import require_token
from RPC.models import DVSAError, DVSAVehicle, DVSAVehiclesAnnual, RPCGrantType
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
    if isinstance(result, DVSAError):
        return result.as_view(), result.major
    return result, 404


@routes.get("/lookup_inline_annual/<string:reg>")
def reg_lookup_inline_annual(reg: str):
    request.log.info("dvsa ves lookup annual", step="begin", registration=reg)
    result = rpc.providers["dvsa"].lookup_annual(reg)
    request.log.info(
        "dvla ves lookup annual",
        step="end",
        registration=reg,
        success=isinstance(result, DVSAVehiclesAnnual),
    )
    if isinstance(result, DVSAVehiclesAnnual):
        return result, 200
    if isinstance(result, DVSAError):
        return result.as_view(), result.major
    return result, 404
