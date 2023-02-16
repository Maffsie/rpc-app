from flask import current_app, request

from RPC.helper import throws
from RPC.roots import Api
from RPC.util.errors import InvalidInputError

routes = Api(url_prefix="/")


@routes.post("/fritzbox_in")
@throws(InvalidInputError)
def fritzbox_s2h():
    current_app.log.notice('{"api":"v2.hooks.fritzbox_in","body":%s}' % request.data)
    return (
        "i have eaten it",
        200,
    )
