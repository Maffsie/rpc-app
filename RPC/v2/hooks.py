from flask import current_app, request

from RPC.util.base import Api

routes = Api(url_prefix="/")


@routes.route("/fritzin")
def fritzbox_s2h(*args, **kwargs):
    current_app.log.verbose(
        msg="wow!", args=args, kwargs=kwargs, reqargs=request.args, requrl=request.url
    )
    return (
        "success?",
        200,
    )
