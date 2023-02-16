from flask import current_app

from RPC.roots import Api

routes = Api()


@routes.get("/devices")
def devicelist():
    return (
        current_app.providers["switchbot"].devices,
        200,
    )


@routes.get("/scenes")
def scenelist():
    return (
        current_app.providers["switchbot"].scenes,
        200,
    )
