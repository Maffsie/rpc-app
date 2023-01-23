"""
RPC.Service.cron - Scheduled tasks
"""

from RPC.vnd.octopus import Octopussy
from RPC.vnd.tailscale import Tailzone


def setup(self):
    self.crontasks = {
        "octopus": Octopussy(self.conf),
        "tailscale": Tailzone(self.conf),
    }
