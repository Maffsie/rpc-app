from PIL import Image, ImageChops
from PIL import ImageFont

from RPC.helper import impose_text
from RPC.util.errors import ImageGenerationError


def inner_render_chad(impose: str, inline_id: int, suffix: int):
    canvas_sz = (585, 525)
    thumb_sz = (150, 150)
    text_font = "resources/fonts/CALIBRI.TTF"
    text_font_sz = 32
    text_begin_xy = (8, 305)
    text_wrap_box = (222, 202)
    calibri = ImageFont.truetype(text_font, text_font_sz)
    jpeg_buf = impose_text(
        impose,
        text_begin_xy,
        text_wrap_box,
        canvas_sz,
        calibri,
        align="right",
        jpegfuck=True,
    )
    with Image.open(jpeg_buf) as blit, Image.open(
        "resources/img/bases/chad.png"
    ) as base:
        base.paste(ImageChops.multiply(blit, base), (0, 0))
        base.save(f"/tmp/r_{inline_id}.{suffix}.jpg", "JPEG", quality=35)
        base.thumbnail(thumb_sz, Image.Resampling.BILINEAR)
        base.save(f"/tmp/r_{inline_id}.{suffix}_t.jpg", "JPEG", quality=75)


def inner_render_rdj(impose: str, inline_id: int, suffix: int):
    canvas_start_sz = (422, 677)
    canvas_stretchfuck_factor = 1.5
    canvas_scalefuck_sz = (
        int(578 / canvas_stretchfuck_factor),
        int(677 / canvas_stretchfuck_factor),
    )
    canvas_stretchbounds_sz = (578, 677)
    canvas_thumb_sz = (150, 150)
    # canvas_final_sz = (600, 677)

    text_font = "resources/fonts/CALIBRI.TTF"
    text_font_sz = 32
    text_begin_xy = (9, 120)
    text_wrap_box = (132, 180)

    calibri = ImageFont.truetype(text_font, text_font_sz)
    jpeg_buf = impose_text(
        impose, text_begin_xy, text_wrap_box, canvas_start_sz, calibri
    )
    with Image.open(jpeg_buf) as distortfuck:
        distortfuck.resize(canvas_scalefuck_sz, Image.Resampling.NEAREST).resize(
            canvas_start_sz, Image.Resampling.BILINEAR
        ).resize(canvas_stretchbounds_sz, Image.Resampling.BILINEAR).save(
            jpeg_buf, "JPEG", quality=7
        )
    with Image.open(jpeg_buf) as blit, Image.open(
        "resources/img/bases/rdj.jpg"
    ) as base:
        base.paste(ImageChops.multiply(blit, base), (0, 0))
        base.save(f"/tmp/r_{inline_id}.{suffix}.jpg", "JPEG", quality=35)
        base.thumbnail(canvas_thumb_sz, Image.Resampling.BILINEAR)
        base.save(f"/tmp/r_{inline_id}.{suffix}_t.jpg", "JPEG", quality=75)


def inline_render_rdj(impose: str, inline_id: str, suffix: int):
    render_rdj(impose, inline_id, suffix)
    prefix = f"https://rpc.puppy.network/v2/memes/renders"
    return ([
        f"{prefix}/{inline_id}.{suffix}",
        f"{prefix}/{inline_id}.{suffix}.t",
    ], (677, 600,), "rdj", suffix)


def inline_render_chad(impose: str, inline_id: str, suffix: int):
    render_chad(impose, inline_id, suffix)
    prefix = f"https://rpc.puppy.network/v2/memes/renders"
    return ([
        f"{prefix}/{inline_id}.{suffix}",
        f"{prefix}/{inline_id}.{suffix}.t",
    ], (585, 525,), "chad", suffix)


def render_rdj(*args, **kwargs):
    try:
        inner_render_rdj(*args, **kwargs)
    except Exception as e:
        raise ImageGenerationError(e)


def render_chad(*args, **kwargs):
    try:
        inner_render_chad(*args, **kwargs)
    except Exception as e:
        raise ImageGenerationError(e)
