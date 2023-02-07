from flask import current_app, request, send_file
from pathlib import Path

from RPC.util.base import Api
from RPC.util.coercion import coerce_type
from RPC.util.decorators import throws
from RPC.util.errors import DishonourableError, ImageGenerationError, InternalOperationalError, InvalidInputError, MissingFileError
from RPC.util.graphics import render_rdj, render_chad
from RPC.util.models import TelegramInlineRequest

routes = Api()


@routes.post("/inline")
@throws(InvalidInputError)
def inline_req():
    """
    payload:
    - chatId: int | None
    - type: str
    - content: str
    - inlineQueryId: int
    - offset: any
    - from:
    -- id: int
    -- is_bot: bool
    -- first_name: str | None
    -- last_name: str | None
    -- username: str | None
    -- language_code: str | None
    - location: any | None
    originalMessage:
    - id: int
    - from:
    -- id: int
    -- is_bot: bool
    -- first_name: str | None
    -- last_name: str | None
    -- username: str | None
    -- language_code: str | None
    - chat_type: str
    - query: str
    - offset: any

    resp.
    payload:
    - chatId: req.
    - type: str = answerInlineQuery
    - content: req.
    - inlineQueryId: req.
    - offset: req.
    - from: req.
    - location: req.
    - results: List[
    -- type: str = photo
    -- id: str
    -- photo_url: str
    -- thumb_url: str
    -- photo_width: int
    -- photo_height: int
    -- title: str
    -- description: str
    ]
    - cache_time: int = 86400
    """
    req: TelegramInlineRequest = None
    try:
        req = TelegramInlineRequest(request)
    except Exception as e:
        raise InternalOperationalError(f"something went wrong: {e}")
    if not req.honour_request:
        raise DishonourableError("fuck you :)")
    return req.jdict


@routes.route("/render/rdj")
@throws(ImageGenerationError, InvalidInputError)
def req_rdj():
    impose = request.args.get("s", "type something already")
    inline_id = coerce_type(request.args.get("i", None), int, need=True)
    render_rdj(impose=impose, inline_id=inline_id)
    return [
        f"{routes.url_prefix}/renders/{inline_id}",
        f"{routes.url_prefix}/renders/{inline_id}.t",
    ]


@routes.route("/render/chad")
@throws(ImageGenerationError, InvalidInputError)
def req_chad():
    impose = request.args.get("s", None)
    inline_id = coerce_type(request.args.get("i", None), int, need=True)
    render_chad(impose=impose, inline_id=inline_id)
    return [
        f"{routes.url_prefix}/renders/{inline_id}",
        f"{routes.url_prefix}/renders/{inline_id}.t",
    ]


@routes.route("/renders/<int:inline_id>.t")
@throws(InvalidInputError, MissingFileError)
def fetch_thumb(inline_id: int):
    fpath = Path(f"/tmp/r_{inline_id}_t.jpg")
    if not (fpath.exists() and fpath.is_file()):
        raise MissingFileError("Rendered thumbnail could not be found.")
    return send_file(fpath)


@routes.route("/renders/<int:inline_id>")
@throws(InvalidInputError, MissingFileError)
def fetch_render(inline_id: int):
    fpath = Path(f"/tmp/r_{inline_id}.jpg")
    if not (fpath.exists() and fpath.is_file()):
        raise MissingFileError("Rendered image could not be found.")
    return send_file(fpath)
