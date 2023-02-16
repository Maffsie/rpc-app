from .app import RPCApp


def create_app():
    return RPCApp(__name__)
