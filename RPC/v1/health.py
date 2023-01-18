from flask import Blueprint, current_app, Response

health = Blueprint("health", __name__, url_prefix="/health")


@health.route("/alive")
def heartbeat_check():
    return Response(response={"status": "alive!"}, status=200)
