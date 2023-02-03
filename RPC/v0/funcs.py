from RPC.util.base import Api

routes = Api()


@routes.route("/voip/sms", methods=["GET"])
def last_sms():
    return "no"


@routes.route("/voip/sms", methods=["POST", "PUT"])
def new_sms():
    return "no"
