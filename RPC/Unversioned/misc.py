from flask import Blueprint, current_app

simple = Blueprint("simple", __name__, url_prefix="/")


@simple.route("/ping")
@simple.route("/ping/js")
@simple.route("/ping/py/2")
def ping():
    return "pong"
