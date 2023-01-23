from flask import current_app

from RPC.util.base import Api

routes = Api(url_prefix="/")


@routes.route("/fritzin")
def fritzbox_s2h(*args, **kwargs):
    current_app.log.verbose(
        msg="wow!",
        extra=[
            args,
            kwargs,
        ],
    )
    return 200
