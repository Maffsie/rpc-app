from flask import Blueprint

from .funcs import functions
from .gen import generators
from .misc import simple
from .public import botapi

unversioned_api = Blueprint("unversioned", __name__, url_prefix="/")
[unversioned_api.register_blueprint(b) for b in (functions, generators, simple, botapi)]
