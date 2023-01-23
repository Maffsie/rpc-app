from RPC.util.base import Api

from .health import routes as health

api = Api()
api.include(
    health,
)
