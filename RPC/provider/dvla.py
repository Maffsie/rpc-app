from json import JSONDecodeError
from re import compile

from RPC.helper import Configurable, WithLogging, throws, validator
from RPC.models import DVLAError, DVLAVehicle
from RPC.roots import IApi
from RPC.util.errors import InternalOperationalError, InvalidInputError

# apparently i am a fool
v_regnum = compile("^[a-zA-Z0-9]+$")


class Doovla(Configurable, WithLogging, IApi):
    app_config = {
        "dvla_apikey": str,
        "dvla_api_endpoint": "https://driver-vehicle-licensing.api.gov.uk",
    }
    errnos = {
        "DVLA_APIKEY": "FDVLAAK",
    }
    errdes = {"FDVLAAK": "No API key present for the DVLA!"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.baseurl = self.app_config.get("dvla_api_endpoint")
        self.headers["user-agent"] = "rpc.dvla-tg/0.9"
        self.headers["x-api-key"] = self.app_config.get("dvla_apikey")

    @throws(InvalidInputError, InternalOperationalError)
    @validator(lambda x: v_regnum.match(x) is not None)
    def lookup(self, reg: str) -> DVLAVehicle | DVLAError:
        try:
            resp = self.post(
                "vehicle-enquiry/v1/vehicles",
                json={
                    "registrationNumber": reg,
                },
            )
            if resp.status_code == 200:
                return DVLAVehicle(resp.json())
            return DVLAError(resp)
        except JSONDecodeError as e:
            raise InternalOperationalError(e.msg)


p_cls = Doovla
