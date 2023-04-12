from enum import Enum, auto

from requests import Response

from RPC.util.coercion import coerce_type
from RPC.util.errors import InternalOperationalError, InvalidInputError


class HasMBID:
    mbid: str

    def __init__(self, json_payload: dict):
        self.mbid = json_payload.get('mbid')
        super().__init__(json_payload)


class ASArtist(HasMBID):
    name: str

    def __init__(self, json_payload: dict):
        super().__init__(json_payload)
        self.name = json_payload.get('#text')


class ASRelease(HasMBID):
    name: str

    def __init__(self, json_payload: dict):
        super().__init__(json_payload)
        self.name = json_payload.get('#text')


class ASTrack(HasMBID):
    title: str
    artist: ASArtist
    album: ASRelease
    loved: bool

    def __init__(self, json_payload: dict):
        super().__init__(json_payload)
        self.title = json_payload.get('name')
        self.artist = ASArtist(json_payload.get('artist'))
        self.album = ASRelease(json_payload.get('album'))
        self.loved = coerce_type(json_payload.get('loved', 0), bool)


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
        self.data = jsn["track"]
