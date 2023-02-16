from quart import jsonify

from RPC.util.base import Api

routes = Api()


@routes.route("/alive")
async def heartbeat_check():
    return (
        jsonify(
            {
                "status": "alive!",
            }
        ),
        200,
    )


"""
TODO
- prometheus metrics exporter
"""
