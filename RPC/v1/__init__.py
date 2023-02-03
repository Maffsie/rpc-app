from RPC.util.base import Api
from RPC.v1.health import routes as health

api = Api()
api.include(
    health,
)
