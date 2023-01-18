from flask import Response, jsonify


def jsonreply(result: dict, hstatus: int = 200) -> Response:
    return Response(response=jsonify(result), status=hstatus)
