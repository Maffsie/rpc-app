from flask import Blueprint

from .funcs import routes as funcs
from .gen import routes as gen
from .misc import routes as misc
from .public import routes as public

api = Blueprint(__name__, __name__, url_prefix="/")
[
    api.register_blueprint(mod)
    for mod in (
        funcs,
        gen,
        misc,
        public,
    )
]
