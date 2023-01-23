from flask import current_app, request

from RPC.util.base import Api

routes = Api(url_prefix="/")


@routes.route(
    "/fritzin",
    methods=[
        "GET",
        "POST",
    ],
)
def fritzbox_s2h():
    current_app.log.verbose(
        "god damn", args=request.args, method=request.method, body=request.data
    )
    return (
        f"success? {request.args}",
        200,
    )
