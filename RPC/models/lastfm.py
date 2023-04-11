from enum import Enum, auto

from requests import Response

from RPC.util.coercion import coerce_type
from RPC.util.errors import InternalOperationalError, InvalidInputError


class ASRecentPlays:
    data: dict
    total: int
    user: str

    def __init__(self, data: Response):
        if not isinstance(data, Response):
            raise InvalidInputError(
                f"Input is not a Response object, but is instead: {type(data)}"
            )
        if data.status_code not in (200,):
            raise InternalOperationalError(
                f"HTTP status {data.status_code} from last.fm!"
            )
        jsn = data.json()["recenttracks"]
        self.total = coerce_type(jsn["@attr"]["total"], int)
        self.user = jsn["@attr"]["user"]
        self.data = jsn["tracks"]


class ASTrack:
    pass
