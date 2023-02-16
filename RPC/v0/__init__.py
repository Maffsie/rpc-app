from RPC.roots import Api

from .funcs import routes as funcs
from .gen import routes as gen
from .misc import routes as misc

api = Api(url_prefix="/")
#api.include(funcs, gen, misc)
