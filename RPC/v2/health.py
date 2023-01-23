from flask import Blueprint, jsonify

routes = Blueprint(__name__, __name__, url_prefix=f"/{__name__}")


@routes.route("/alive")
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
