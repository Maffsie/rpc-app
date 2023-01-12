from flask import Flask


def create_app():
    app = Flask(__name__)

    from RPC.Unversioned import unversioned_api
    from RPC.v1 import v1_api

    app.register_blueprint(unversioned_api)
    app.register_blueprint(v1_api)

    return app
