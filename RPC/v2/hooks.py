from flask import current_app, request

from RPC.util.base import Api

routes = Api(url_prefix="/")


@routes.route("/fritzin")
def fritzbox_s2h():
    print(f"/fritzin! args={request.args} url={request.url}")
    return (
        "success?",
        200,
    )
