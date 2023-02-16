from RPC.roots import Api

routes = Api(url_prefix="/")


@routes.get("/ping")
@routes.get("/ping/js")
@routes.get("/ping/py/2")
def ping():
    return "pong"
