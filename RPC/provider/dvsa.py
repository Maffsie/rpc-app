from json import JSONDecodeError
from re import compile

from RPC.helper import Configurable, WithLogging, throws, validator
from RPC.models import DVLAError, DVLAVehicle
from RPC.roots import IApi
from RPC.util.errors import InternalOperationalError, InvalidInputError

# apparently i am a fool
v_regnum = compile("^[a-zA-Z0-9]+$")


class Doovsa(Configurable, WithLogging, IApi):
    app_config = {
        "dvsa_apikey": str,
        "dvsa_api_endpoint": "https://beta.check-mot.service.gov.uk",
    }
    errnos = {
        "DVSA_APIKEY": "FDVSAAK",
    }
    errdes = {"FDVSAAK": "No API key present for the DVSA!"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.baseurl = self.app_config.get("dvsa_api_endpoint")
        self.headers["user-agent"] = "rpc.dvsa-tg/0.9"
        self.headers["x-api-key"] = self.app_config.get("dvsa_apikey")

    @throws(InvalidInputError, InternalOperationalError)
    @validator(lambda x: v_regnum.match(x) is not None)
    def lookup_single(self, reg: str) -> DVLAVehicle | DVLAError:
        try:
            resp = self.get(
                "trade/vehicles/mot-tests",
                params={
                    "registration": reg,
                },
            )
            if resp.status_code == 200:
                return DVSAVehicle(resp.json())
            return DVSAError(resp)
        except JSONDecodeError as e:
            raise InternalOperationalError(e.msg)


p_cls = Doovsa
