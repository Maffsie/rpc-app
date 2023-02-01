from json import JSONDecodeError
from re import compile

from RPC.util.decorators import throws, validator
from RPC.util.errors import InvalidInputError, InternalOperationalError
from RPC.util.helpers import Configurable
from RPC.util.layers import WithLogging, IApi
from RPC.util.models import DVLAVehicle

v_regnum = compile("^[a-np-zA-NP-Z0-9]+$")


class Doovla(IApi, WithLogging, Configurable):
    app_config = {
        "doovla_api_key": str,
        "doovla_api_endpoint": "https://driver-vehicle-licensing.api.gov.uk",
    }
    errnos = {
        "DOOVLA_API_KEY": "FDVLAAK",
    }
    errdes = {
        "FDVLAAK": "No API key present for the DVLA!"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.baseurl = self.app_config.get("doovla_api_endpoint")
        self.headers["x-api-key"] = self.app_config.get("doovla_api_key")

    @throws(InvalidInputError, InternalOperationalError)
    @validator(lambda x: v_regnum.match(x))
    def lookup(self, reg: str) -> DVLAVehicle | str:
        try:
            resp = self.post("vehicle-enquiry/v1/vehicles", data={
                "registrationNumber": reg,
            })
            match resp.status_code:
                case 200:
                    return DVLAVehicle(resp.json())
                case 404:
                    return "Registration number not recognised. If you know the registration " \
                           "number to be accurate and previously valid and registered, " \
                           "the vehicle may have been scrapped."
                case _:
                    raise InternalOperationalError(f"Status {resp.status_code} from DVLA", resp)
        except JSONDecodeError as e:
            raise InternalOperationalError(e.msg)
