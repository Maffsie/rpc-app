from RPC.util.base import Api

from RPC.v2.dvla import routes as dvla_ves
from RPC.v2.health import routes as health
from RPC.v2.hooks import routes as hooks

api = Api()
api.include(dvla_ves, health, hooks)
