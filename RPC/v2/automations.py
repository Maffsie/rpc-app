from quart import current_app

from RPC.util.base import Api

routes = Api()


@routes.route("/devices")
async def devicelist():
    return (
        await current_app.providers["switchbot"].devices(),
        200,
    )


@routes.route("/scenes")
async def scenelist():
    return (
        await current_app.providers["switchbot"].scenes(),
        200,
    )
