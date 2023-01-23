from flask import Blueprint

routes = Blueprint(__name__, __name__, url_prefix=f"/{__name__}")


@routes.route("/voip/sms", methods=["GET"])
def last_sms():
    return "no"


@routes.route("/voip/sms", methods=["POST", "PUT"])
def new_sms():
    return "no"
