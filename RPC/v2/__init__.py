from RPC.util.base import Api

from .health import routes as health
from .hooks import routes as hooks

api = Api()
api.include(health, hooks)
