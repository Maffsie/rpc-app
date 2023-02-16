from RPC.roots import Api

routes = Api()


@routes.get("/voip/sms")
def last_sms():
    return "no"


@routes.post("/voip/sms")
@routes.put("/voip/sms")
def new_sms():
    return "no"
