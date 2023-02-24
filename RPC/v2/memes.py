from pathlib import Path

from flask import request, send_file

from RPC.helper import throws
from RPC.models.telegram import TelegramInlineRequest
from RPC.roots import Api, RPCRequest
from RPC.util.errors import (
    DishonourableError,
    InternalOperationalError,
    InvalidInputError,
    MissingFileError,
)
from RPC.util.graphics import inline_render_chad, inline_render_rdj

request: RPCRequest
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
    request.log.info("inline memes", step="begin")
    req: TelegramInlineRequest
    try:
        req = TelegramInlineRequest(request)
        request.log.info(
            "inline memes",
            step="parsed",
            requestor_id=req.from_id,
            requestor_uname=req.from_uname,
            requestor_bot=req.from_bot,
            inline_id=req.inline_id,
            honour=req.honour_request,
        )
    except Exception as e:
        raise InternalOperationalError(f"something went wrong: {e}")
    if not req.honour_request:
        raise DishonourableError("fuck you :)")
    req.append_response(
        *inline_render_chad(impose=req.content, inline_id=req.inline_id, suffix=0)
    )
    req.append_response(
        *inline_render_rdj(impose=req.content, inline_id=req.inline_id, suffix=1)
    )
    request.log.info(
        "inline memes",
        step="end",
        requestor_id=req.from_id,
        requestor_uname=req.from_uname,
        requestor_bot=req.from_bot,
        inline_id=req.inline_id,
        responses=len(req.responses),
    )
    return req.jdict


@routes.get("/renders/<int:inline_id>.<int:suffix>.t")
@throws(InvalidInputError, MissingFileError)
def fetch_thumb(inline_id: int, suffix: int):
    fpath = Path(f"/tmp/r_{inline_id}.{suffix}_t.jpg")
    request.log.info("get thumb", step="begin", inline_id=inline_id, suffix=suffix)
    if not (fpath.exists() and fpath.is_file()):
        raise MissingFileError("Rendered thumbnail could not be found.")
    request.log.info("get thumb", step="end", inline_id=inline_id, suffix=suffix)
    return send_file(fpath)


@routes.get("/renders/<int:inline_id>.<int:suffix>")
@throws(InvalidInputError, MissingFileError)
def fetch_render(inline_id: int, suffix: int):
    fpath = Path(f"/tmp/r_{inline_id}.{suffix}.jpg")
    request.log.info("get render", step="begin", inline_id=inline_id, suffix=suffix)
    if not (fpath.exists() and fpath.is_file()):
        raise MissingFileError("Rendered image could not be found.")
    request.log.info("get render", step="end", inline_id=inline_id, suffix=suffix)
    return send_file(fpath)
