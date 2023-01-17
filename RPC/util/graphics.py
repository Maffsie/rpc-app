from io import BytesIO
from typing import Optional, Tuple

from PIL import Image, ImageChops
from PIL import ImageColor as ImageColour
from PIL import ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

from .errors import ImageGenerationError


def wrap_text(
    font: FreeTypeFont, text: str, max_width: int, direction: str = "ltr"
) -> str:
    words = text.split()

    lines: list[str] = [""]
    curr_line_width = 0

    for word in words:
        if len(word) > 20:
            lines[-1] = "word too long"
        else:
            if curr_line_width == 0:
                word_width = font.getlength(word, direction)
                # if word_width > max_width:
                # while True:
                #    for ch in range(len(word), 1, -1):
                #        if font.getlength(word[0:ch], direction) <= max_width:
                #            lines.append(word[0:ch])
                #            word = word.partition(word[0:ch])[2]
                #            break
                #    match len(word):
                #        case 0:
                #            break
                #        case 1:
                #            lines.append(word)
                #            break

                lines[-1] = word
                curr_line_width = word_width
            else:
                new_line_width = font.getlength(f"{lines[-1]} {word}", direction)

                if new_line_width > max_width:
                    # Word is too long to fit on the current line
                    word_width = font.getlength(word, direction)

                    # Put the word on the next line
                    lines.append(word)
                    curr_line_width = word_width
                else:
                    # Put the word on the current line
                    lines[-1] = f"{lines[-1]} {word}"
                    curr_line_width = new_line_width

    return "\n".join(lines)


def try_fit_text(
    font: FreeTypeFont,
    text: str,
    max_width: int,
    max_height: int,
    spacing: int = 4,
    direction: str = "ltr",
) -> Optional[str]:

    words = text.split()

    line_height = font.size

    if line_height > max_height:
        # The line height is already too big
        return None

    lines: list[str] = [""]
    curr_line_width = 0

    for word in words:
        if curr_line_width == 0:
            word_width = font.getlength(word, direction)

            if word_width > max_width:
                # Word is longer than max_width
                return None

            lines[-1] = word
            curr_line_width = word_width
        else:
            new_line_width = font.getlength(f"{lines[-1]} {word}", direction)

            if new_line_width > max_width:
                # Word is too long to fit on the current line
                word_width = font.getlength(word, direction)
                new_num_lines = len(lines) + 1
                new_text_height = (new_num_lines * line_height) + (
                    new_num_lines * spacing
                )

                if word_width > max_width or new_text_height > max_height:
                    # Word is longer than max_width, and
                    # adding a new line would make the text too tall
                    return None

                # Put the word on the next line
                lines.append(word)
                curr_line_width = word_width
            else:
                # Put the word on the current line
                lines[-1] = f"{lines[-1]} {word}"
                curr_line_width = new_line_width

    return "\n".join(lines)


def fit_text(
    font: FreeTypeFont,
    text: str,
    max_width: int,
    max_height: int,
    spacing: int = 4,
    scale_factor: float = 0.8,
    max_iterations: int = 5,
    direction: str = "ltr",
) -> Tuple[FreeTypeFont, str]:
    initial_font_size = font.size
    trial_font = font.font_variant(size=initial_font_size)

    for i in range(max_iterations):
        trial_font_size = int(initial_font_size * pow(scale_factor, i))
        trial_font = font.font_variant(size=trial_font_size)

        wrapped_text = try_fit_text(
            trial_font,
            text,
            max_width,
            max_height,
            spacing,
            direction,
        )

        if wrapped_text:
            return (trial_font, wrapped_text)

    wrapped_text = wrap_text(trial_font, text, max_width, direction)

    return (trial_font, wrapped_text)


def inner_render_rdj(impose: str, id: int):
    canvas_start_sz = (422, 677)
    canvas_stretchfuck_factor = 1.5
    canvas_scalefuck_sz = (
        int(578 / canvas_stretchfuck_factor),
        int(677 / canvas_stretchfuck_factor),
    )
    canvas_stretchbounds_sz = (578, 677)
    canvas_thumb_sz = (150, 150)
    # canvas_final_sz = (600, 677)

    text_font = "resources/CALIBRI.TTF"
    text_font_sz = 32
    text_begin_xy = (9, 120)
    text_wrap_box = (132, 180)

    jpeg_buf = BytesIO()

    with Image.new("RGB", canvas_start_sz, ImageColour.getrgb("white")) as canvas_tx:
        calibri = ImageFont.truetype(text_font, text_font_sz)
        pen = ImageDraw.Draw(canvas_tx)

        (_, wrapped_text) = fit_text(
            font=calibri,
            text=impose,
            max_height=9999999999999999999999999999999999999999999999999,
            max_width=text_wrap_box[0],
            scale_factor=1.0,
            max_iterations=1,
            spacing=3,
        )
        pen.multiline_text(
            text_begin_xy,
            wrapped_text,
            font=calibri,
            fill=ImageColour.getrgb("black"),
            align="center",
        )

        canvas_tx.resize(canvas_scalefuck_sz, Image.Resampling.NEAREST).resize(
            canvas_start_sz, Image.Resampling.BILINEAR
        ).resize(canvas_stretchbounds_sz, Image.Resampling.BILINEAR).save(
            jpeg_buf, "JPEG", quality=7
        )
    with Image.open(jpeg_buf) as blit, Image.open("resources/_.jpg") as base:
        base.paste(ImageChops.multiply(blit, base), (0, 0))
        base.save(f"/tmp/{id}.jpg", "JPEG", quality=35)
        base.thumbnail(canvas_thumb_sz, Image.Resampling.BILINEAR)
        base.save(f"/tmp/{id}_t.jpg", "JPEG", quality=75)


def render_rdj(*args, **kwargs):
    try:
        inner_render_rdj(*args, **kwargs)
    except Exception as e:
        raise ImageGenerationError(e)
