from flask import Blueprint, current_app, jsonify

health = Blueprint("health", __name__, url_prefix="/health")


@health.route("/alive")
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
