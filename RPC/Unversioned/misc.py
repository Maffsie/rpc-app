from flask import Blueprint

routes = Blueprint(__name__, __name__, url_prefix="/")


@routes.route("/ping")
@routes.route("/ping/js")
@routes.route("/ping/py/2")
def ping():
    return "pong"
