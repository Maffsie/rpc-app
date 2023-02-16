from flask import jsonify

from RPC.roots import Api

routes = Api()


@routes.get("/alive")
def heartbeat_check():
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
