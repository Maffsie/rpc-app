from flask import Blueprint

from .health import health

v1_api = Blueprint("v1", __name__, url_prefix="/v1")
[v1_api.register_blueprint(api) for api in (health,)]
