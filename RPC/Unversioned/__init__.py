from RPC.util.base import Api

from .funcs import routes as funcs
from .gen import routes as gen
from .misc import routes as misc
from .public import routes as public

api = Api(url_prefix="/")
api.include(funcs, gen, misc, public)
