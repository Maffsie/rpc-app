from flask import Blueprint

from .funcs import functions
from .gen import generators
from .misc import simple

unversioned_api = Blueprint("unversioned", __name__, url_prefix="/")
unversioned_api.register_blueprint(functions)
unversioned_api.register_blueprint(generators)
unversioned_api.register_blueprint(simple)
