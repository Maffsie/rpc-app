from flask import current_app

from RPC.util.base import Api

routes = Api()


@routes.route("/scenes")
def scenelist():
    return (
        current_app.providers["switchbot"].scenes(),
        200,
    )
