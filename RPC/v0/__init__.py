from RPC.util.base import Api

from RPC.v0.funcs import routes as funcs
from RPC.v0.gen import routes as gen
from RPC.v0.misc import routes as misc
from RPC.v0.public import routes as public

api = Api(url_prefix="/")
api.include(funcs, gen, misc, public)
