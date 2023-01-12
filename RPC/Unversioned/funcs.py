from flask import Blueprint, current_app, request

functions = Blueprint("funcs", __name__, url_prefix="/functions")


@functions.route("/voip/sms", methods=["GET"])
def last_sms():
    return "no"


@functions.route("/voip/sms", methods=["POST", "PUT"])
def new_sms():
    return "no"
