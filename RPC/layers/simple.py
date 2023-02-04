import logging

from requests import Session


class WithLogging:
    log: logging.Logger = None

    def __init__(self, *args, ctx: str | None = None, **kwargs):
        self.log = logging.getLogger(name=ctx)
        super().__init__(*args, **kwargs)


class IApi(Session):
    baseurl: str = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def request(self, method, url, *args, **kwargs):
        return super().request(
            method=method, url=f"{self.baseurl}/{url}", *args, **kwargs
        )
