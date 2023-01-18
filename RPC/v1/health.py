from flask import Blueprint, current_app

from RPC.util.response import jsonreply

health = Blueprint("health", __name__, url_prefix="/health")


@health.route("/alive")
def heartbeat_check():
    return jsonreply(
        {
            "status": "alive!",
        }
    )
