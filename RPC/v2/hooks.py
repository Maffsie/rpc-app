from flask import current_app, request

from RPC.util.base import Api
from RPC.util.decorators import throws
from RPC.util.errors import InvalidInputError

routes = Api(url_prefix="/")


@routes.route(
    "/fritzbox_in",
    methods=[
        "POST",
    ],
)
@throws(
    InvalidInputError,
)
def fritzbox_s2h():
    current_app.log.verbose("fuckin", request.headers)
    input_json = None
    try:
        input_json = request.json
    except Exception as e:
        raise InvalidInputError(f"bad boy.........{e}")
    current_app.log.notice(
        f"can you believe {input_json['addresses']['from']['address']} would {input_json['subject']}"
    )
    return (
        f"thanks for your data it yumy",
        200,
    )
