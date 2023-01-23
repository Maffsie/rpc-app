from flask import Blueprint

from .funcs import functions
from .gen import generators
from .misc import simple
from .public import botapi

api = Blueprint(__name__, __name__, url_prefix="/")
[api.register_blueprint(mod) for mod in (functions, generators, simple, botapi)]
