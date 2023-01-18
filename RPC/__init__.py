from .app import RPCApp


def create_app():
    rpc = RPCApp(__name__)

    from RPC.Unversioned import unversioned_api
    from RPC.v1 import v1_api

    [rpc.register_blueprint(b) for b in (unversioned_api, v1_api)]

    return rpc
