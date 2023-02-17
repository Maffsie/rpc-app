import logging
import sqlite3

from influxdb import InfluxDBClient

from RPC.helper import load_conf_static


class WithDBConf:
    dbo_conf = {}

    def __init__(
        self, *args, db: str | None = None, dbvar: str | None = None, **kwargs
    ):
        # TODO: This is messy as fuck
        if db is None or db == "" and dbvar is not None and dbvar != "":
            self.dbo_conf[dbvar] = str
        self.dbo_conf = load_conf_static(self.dbo_conf, {}, {})
        db = self.dbo_conf.get(dbvar, db)
        if db is None or db == "":
            raise Exception("why")
        self.dbo_conf["_db"] = db
        super().__init__(*args, **kwargs)


class WithInfluxDB(WithDBConf):
    dbi: InfluxDBClient = None
    dbo_conf = {
        "db_influx_host": str,
        "db_influx_port": 8086,
        "db_influx_tls": False,
        "db_influx_verifytls": False,
        "db_influx_auth": bool,
        "db_influx_user": str,
        "db_influx_pass": str,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbi = InfluxDBClient(
            host=self.dbo_conf.get("db_influx_host"),
            port=self.dbo_conf.get("db_influx_port"),
            ssl=self.dbo_conf.get("db_influx_tls"),
            verify_ssl=self.dbo_conf.get("db_influx_tlsverify"),
            database=self.dbo_conf.get("_db"),
        )


class WithSQLiteDB(WithDBConf):
    dbo_conf = {}

    def _with_db(self) -> sqlite3.Connection:
        return sqlite3.connect(database=self.dbo_conf.get("_db"))


class WithLogging:
    """
    Layer to provide logging for subclasses
    """

    log: logging.Logger = None

    def __init__(self, *args, ctx: str | None = None, **kwargs):
        self.log = logging.getLogger(name=ctx)
        super().__init__(*args, **kwargs)
