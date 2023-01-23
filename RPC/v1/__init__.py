from flask import Blueprint

from .health import routes as health

api = Blueprint(__name__, __name__, url_prefix=f"/{__name__}")
[api.register_blueprint(mod) for mod in (health,)]
