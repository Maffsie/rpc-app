from RPC.roots import Api

from .automations import routes as automations
from .dvla import routes as dvla_ves
from .health import routes as health
from .hooks import routes as hooks
from .memes import routes as memes

api = Api()
#api.include(automations, dvla_ves, health, hooks, memes)
