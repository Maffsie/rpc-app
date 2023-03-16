from json import JSONDecodeError
from re import compile

from requests import Response

from RPC.helper import Configurable, WithLogging, throws
from RPC.models import ASRecentPlays, ASTrack
from RPC.roots import IApi
from RPC.util.errors import InternalOperationalError, InvalidInputError


class AudioScrobble(Configurable, WithLogging, IApi):
    app_config = {
        "lastfm_api_key": str,
        "lastfm_api_endpoint": "https://ws.audioscrobbler.com/2.0",
    }
    errnos = {
        "LASTFM_API_KEY": "FLFMAK",
    }
    errdes = {"FLFMAK": "No API key present for the Last.fm API!"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.baseurl = self.app_config.get("lastfm_api_endpoint")
        self.headers["user-agent"] = "rpc.lastfm-client/0.9"

    def request(self, method, url="", *args, **kwargs):
        return super().request(method, url, *args, **kwargs)

    def read(self, method, **kwargs):
        return self.request("GET", params={
            "method": method,
            "format": "json",
            "api_key": self.app_config.get("lastfm_api_key"),
            **kwargs
        })

    def write(self, method, **kwargs) -> Response:
        return self.request("POST", data={
            "method": method,
            "format": "json",
            "api_key": self.app_config.get("lastfm_api_key"),
            **kwargs
        })

    @throws(InvalidInputError, InternalOperationalError)
    def recent_scrobbles(self, user: str) -> ASRecentPlays:
        try:
            return ASRecentPlays(self.read(method="user.getrecenttracks", user=user, extended=1))
        except JSONDecodeError as e:
            raise InternalOperationalError(e.msg)


p_cls = AudioScrobble
