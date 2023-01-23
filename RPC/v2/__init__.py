from flask import Blueprint

from .health import health

v2_api = Blueprint("v2", __name__, url_prefix="/v2")
[v2_api.register_blueprint(api) for api in (health,)]
