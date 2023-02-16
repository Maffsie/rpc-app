from quart import current_app

from RPC.util.base import Api

routes = Api()


@routes.route("/devices")
def devicelist():
    return (
        current_app.providers["switchbot"].devices(),
        200,
    )


@routes.route("/scenes")
def scenelist():
    return (
        current_app.providers["switchbot"].scenes(),
        200,
    )
