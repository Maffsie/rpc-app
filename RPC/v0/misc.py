from RPC.util.base import Api

routes = Api(url_prefix="/")


@routes.route("/ping")
@routes.route("/ping/js")
@routes.route("/ping/py/2")
async def ping():
    return "pong"
