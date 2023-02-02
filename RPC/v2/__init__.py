from RPC.util.base import Api

from .dvla import routes as dvla_ves
from .health import routes as health
from .hooks import routes as hooks

api = Api()
api.include(dvla_ves, health, hooks)
