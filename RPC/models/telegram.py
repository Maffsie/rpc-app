from dataclasses import dataclass

from flask import Request

from RPC.roots import RPCRequest
from RPC.util.coercion import coerce_type


@dataclass
class TelegramInvocableResult:
    url: str
    width: int
    height: int
    hname: str


class TelegramInlineRequest:
    inline_id: str
    chat_id: int | None
    content: str
    request_type: str
    from_id: int
    from_bot: bool
    from_uname: str | None
    from_obj: dict

    responses: list

    def __init__(self, request: RPCRequest | Request):
        reqj = request.json
        self.inline_id = reqj["inlineQueryId"]
        self.chat_id = coerce_type(reqj.get("chatId", None), int)
        self.content = reqj["content"]
        self.request_type = reqj["type"]
        self.from_obj = reqj["from"]
        self.from_id = coerce_type(reqj["from"]["id"], int, need=True)
        self.from_bot = coerce_type(reqj["from"]["is_bot"], bool, need=True)
        self.from_uname = reqj["from"]["username"]
        self.responses = []

    @property
    def honour_request(self):
        # No bots.
        if self.from_bot:
            return False
        return True

    def append_response(self, urls: list[str], res: (int, int), desc: str, res_id: int):
        self.responses.append(
            {
                "type": "photo",
                "id": f"{self.inline_id}.{res_id}",
                "photo_url": urls[0],
                "thumb_url": urls[1],
                "photo_width": res[0],
                "photo_height": res[1],
                "title": desc,
                "description": desc,
            }
        )

    @property
    def jdict(self) -> dict:
        return {
            "chatId": self.chat_id,
            "type": "answerInlineQuery",
            "content": self.content,
            "inlineQueryId": self.inline_id,
            "offset": "",
            "from": {**self.from_obj},
            "cache_time": 86400,
            "results": self.responses,
        }
