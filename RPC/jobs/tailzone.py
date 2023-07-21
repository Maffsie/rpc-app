from RPC import RPCApp
from RPC.provider.tailscale import Tailzone

from celery import shared_task as job
from flask import current_app as rpc

rpc: RPCApp


@job
def update_tailzone():
    rpc.log.info("what")
    tz: Tailzone = rpc.providers.get("tailscale")
    print(tz.tailzone())
