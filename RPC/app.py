from importlib import import_module
from pkgutil import iter_modules

from flask import Flask
from celery import Celery, Task

from RPC.provider import get_providers

from .roots import Base, RPCRequest


class RPCApp(Base, Flask):
    app_config = {
        "debug": False,
        "base_uri": str,
        "celery_broker": str,
        "celery_persist": str,
    }
    providers = {}
    services = {}

    job_processor: Celery
    request_class = RPCRequest

    def __init__(self, appid: str):
        super().__init__(None, appid)
        # Override the Flask logger
        self.logger = self.log.get_logger(__name__)
        self.providers = get_providers()
        self.setup_services()
        self.find_routes()
        self.config.from_mapping(
            CELERY=dict(
                broker_url=self.app_config.get("celery_broker"),
                result_backend=self.app_config.get("celery_persist"),
            )
        )
        self.setup_job_processor()

    def setup_job_processor(self):
        class RPCTask(Task):
            def __call__(subself, *args, **kwargs):
                with self.app_context():
                    subself.run(*args, **kwargs)

        self.job_processor = Celery(__name__, task_cls=RPCTask)
        self.job_processor.config_from_object(self.config["CELERY"])
        self.job_processor.set_default()
        self.extensions["celery"] = self.job_processor

    def register_blueprint(self, blueprint, *args, **kwargs):
        self.log.info(
            f"Registering base API {blueprint.name} on {blueprint.url_prefix}"
        )
        super().register_blueprint(blueprint, *args, **kwargs)

    def find_routes(self):
        [
            self.register_blueprint(getattr(api, "api"))
            for api in [
                import_module(name)
                for _, name, _ in iter_modules([self.root_path], "RPC.")
                if name.startswith("RPC.v")
            ]
            if hasattr(api, "api")
        ]

    def setup_services(self):
        # TODO: dynamic loader for services
        pass
