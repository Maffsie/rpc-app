import logging

from influxdb import InfluxDBClient
from requests import Session

from RPC.util.helpers import load_conf_static


class WithInfluxDB:
    db: InfluxDBClient = None
    db_config = {
        "data_influx_host": str,
        "data_influx_port": 8086,
        "data_influx_tls": False,
        "data_influx_verifytls": False,
        "data_influx_auth": bool,
        "data_influx_user": str,
        "data_influx_pass": str,
    }

    def __init__(
        self, *args, db: str | None = None, dbvar: str | None = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        # TODO: This is messy as fuck
        if db is None or db == "" and dbvar is not None and dbvar != "":
            self.db_config[dbvar] = str
        self.db_config = load_conf_static(self.db_config, {}, {})
        db = self.db_config.get(dbvar, db)
        if db is None or db == "":
            raise Exception("why")
        self.db = InfluxDBClient(
            host=self.db_config.get("data_influxdb_host"),
            port=self.db_config.get("data_influxdb_port"),
            ssl=self.db_config.get("data_influxdb_tls"),
            verify_ssl=self.db_config.get("data_influxdb_tlsverify"),
            database=db,
        )


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
