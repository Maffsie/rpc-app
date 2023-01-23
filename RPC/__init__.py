from .app import RPCApp


def create_app():
    rpc = RPCApp(__name__)

    from RPC.Unversioned import api as v0
    from RPC.v1 import api as v1
    from RPC.v2 import api as v2

    [rpc.register_blueprint(b) for b in (v0, v1, v2)]

    return rpc
