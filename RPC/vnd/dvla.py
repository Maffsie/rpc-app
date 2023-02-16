from json import JSONDecodeError
from re import compile

from RPC.layers import WithLogging
from RPC.util.base import IApi
from RPC.util.decorators import throws, validator
from RPC.util.errors import InternalOperationalError, InvalidInputError
from RPC.util.helpers import Configurable
from RPC.util.models import DVLAError, DVLAVehicle

# apparently i am a fool
v_regnum = compile("^[a-zA-Z0-9]+$")


class Doovla(Configurable, WithLogging, IApi):
    app_config = {
        "doovla_api_key": str,
        "doovla_api_endpoint": "https://driver-vehicle-licensing.api.gov.uk",
    }
    errnos = {
        "DOOVLA_API_KEY": "FDVLAAK",
    }
    errdes = {"FDVLAAK": "No API key present for the DVLA!"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.baseurl = self.app_config.get("doovla_api_endpoint")
        self.headers["x-api-key"] = self.app_config.get("doovla_api_key")

    @throws(InvalidInputError, InternalOperationalError)
    @validator(lambda x: v_regnum.match(x) is not None)
    def lookup(self, reg: str) -> DVLAVehicle | str:
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
