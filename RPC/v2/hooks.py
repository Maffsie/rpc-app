from quart import current_app, request

from RPC.util.base import Api
from RPC.util.decorators import throws
from RPC.util.errors import InvalidInputError

routes = Api(url_prefix="/")


@routes.route(
    "/fritzbox_in",
    methods=[
        "POST",
    ],
)
@throws(
    InvalidInputError,
)
async def fritzbox_s2h():
    current_app.log.notice('{"api":"v2.hooks.fritzbox_in","body":%s}' % await request.data)
    return (
        "i have eaten it",
        200,
    )
