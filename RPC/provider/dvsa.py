from json import JSONDecodeError
from re import compile

from RPC.helper import Configurable, WithLogging, throws, validator
from RPC.models import DVSAError, DVSAVehicle
from RPC.roots import IApi
from RPC.util.errors import InternalOperationalError, InvalidInputError

from .dvla import v_regnum


class Doovsa(Configurable, WithLogging, IApi):
    app_config = {
        "dvsa_api_key": str,
        "dvsa_api_endpoint": "https://beta.check-mot.service.gov.uk",
    }
    errnos = {
        "DVSA_API_KEY": "FDVSAAK",
    }
    errdes = {"FDVSAAK": "No API key present for the DVSA!"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.baseurl = self.app_config.get("dvsa_api_endpoint")
        self.headers["user-agent"] = "rpc.dvsa-tg/0.9"
        self.headers["x-api-key"] = self.app_config.get("dvsa_api_key")

    @throws(InvalidInputError, InternalOperationalError)
    @validator(lambda x: v_regnum.match(x) is not None)
    def lookup_single(self, reg: str) -> DVSAVehicle | DVSAError:
        try:
            resp = self.get(
                "trade/vehicles/mot-tests",
                params={
                    "registration": reg,
                },
            )
            if resp.status_code == 200:
                return DVSAVehicle(resp.json()[0])
            return DVSAError(resp)
        except JSONDecodeError as e:
            raise InternalOperationalError(e.msg)


p_cls = Doovsa
