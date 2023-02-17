from RPC.helper import Configurable, WithLogging
from RPC.roots import IApi


class Switchbot(Configurable, WithLogging, IApi):
    baseurl = "https://api.switch-bot.com/v1.0"

    app_config = {
        "switchbot_api_key": str,
    }
    errnos = {
        "SWITCHBOT_API_KEY": "FSBAKR",
    }
    errdes = {
        "FSBAKR": "Switchbot API key required!",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers["Authorization"] = self.app_config.get("doovla_api_key")

    @property
    def devices(self) -> [dict]:
        return []

    def device(self, device_id: str) -> dict:
        # /devices/{device_id}/status
        return {}

    def command(self, device_id: str, cmd: str) -> dict:
        return {}

    @property
    def scenes(self) -> [dict]:
        res = self.get("/scenes")
        return [
            {"id": scene["sceneId"], "name": scene["sceneName"]}
            for scene in res.json()["body"]
        ]

    def execute(self, scene_id: str) -> bool:
        res = self.post(f"/scenes/{scene_id}/execute")
        return res.json()["message"] == "success"
