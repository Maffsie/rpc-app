from pathlib import Path

from flask import request, send_file

from RPC.util.base import Api
from RPC.util.coercion import coerce_type
from RPC.util.decorators import throws
from RPC.util.errors import ImageGenerationError, InvalidInputError, MissingFileError
from RPC.util.graphics import render_rdj

routes = Api()


@routes.route("/get_last")
@throws(InvalidInputError, MissingFileError)
def get_render():
    req_id = coerce_type(request.args.get("i", None), int, need=True)
    fpath = Path(f"/tmp/{req_id}.jpg")
    if fpath.exists() and fpath.is_file():
        return send_file(fpath)
    else:
        raise MissingFileError("woe betide, yon image be missing.")


@routes.route("/get_last_t")
@throws(InvalidInputError, MissingFileError)
def get_render_thumb():
    req_id = coerce_type(request.args.get("i", None), int, need=True)
    fpath = Path(f"/tmp/{req_id}_t.jpg")
    if fpath.exists() and fpath.is_file():
        return send_file(fpath)
    else:
        raise MissingFileError("woe betide, yon thumbnail be missing.")


@routes.route("/there_isare_outside_my_")
@throws(ImageGenerationError, InvalidInputError)
def render():
    req_id = coerce_type(request.args.get("i", None), int, need=True)
    render_rdj(impose=request.args.get("s", "type something already"), id=req_id)
    return [f"/public/get_last?i={req_id}", f"/public/get_last_t?i={req_id}"]