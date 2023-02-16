from datetime import datetime, timedelta
from urllib import parse

from dateutil import parser
from requests import get

from RPC.helper import Configurable, WithInfluxDB, WithLogging


class Octopussy(WithInfluxDB, WithLogging, Configurable):
    dt_from = datetime.now() - timedelta(days=30)
    dt_to = datetime.now()
    app_config = {
        "cron_octopus_period": int,
        "cron_octopus_apinum": 1000,
        "vnd_octopus_apikey": str,
        "vnd_octopus_elecsn": str,
        "vnd_octopus_gassn": str,
        "vnd_octopus_gasfac": float(0),
        "vnd_octopus_mpan": str,
        "vnd_octopus_mprn": str,
    }

    uris = {
        "electricity": [
            "https://api.octopus.energy/v1/electricity-meter-points/%s/meters/%s/consumption/",
            "cron_octopus_mpan",
            "cron_octopus_elecsn",
        ],
        "gas": [
            "https://api.octopus.energy/v1/gas-meter-points/%s/meters/%s/consumption/",
            "cron_octopus_mprn",
            "cron_octopus_gassn",
        ],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ctx="vnd.Octopussy", dbvar="cron_octopus_db", **kwargs)

    def load_series(self, uri, dt_from=None, dt_to=None, page=None):
        """
        Fetch all datapoints from Octopus, using recursion to handle pagination
        """
        params = {
            "period_from": dt_from if dt_from else self.dt_from,
            "period_to": dt_to if dt_to else self.dt_to,
            "page_size": self.app_config.get("cron_octopus_apinum"),
        }
        if page is not None:
            params["page"] = page
        resp = get(
            uri, params=params, auth=(self.app_config.get("octopus_api_key"), "")
        )
        resp.raise_for_status()
        res = resp.json()
        ret = res.get("results", [])
        self.log.info(
            f"Got {len(ret)} result(s) for range {dt_from} to {dt_to} (page {page})",
        )
        if res["next"]:
            p_next = parse.urlparse(res["next"]).query
            ret += self.load_series(
                uri, dt_from, dt_to, page=parse.parse_qs(p_next)["page"][0]
            )
        return ret

    def load_dt(self, series):
        """
        Load the most recent datapoint for the given series from InfluxDB.
        If the most recent datapoint is not available or the series is formed differently,
        the series will be completely discarded and the default from date will be used.
        """
        dt_from = self.dt_from
        dt_to = self.dt_to
        resp = self.db.query(
            f"SELECT time, raw_consumption FROM {series} ORDER BY time DESC LIMIT 1"
        )
        if (
            not self.app_config.get("influxdb_reset_db_contents", False)
            and "series" in resp.raw
            and "values" in resp.raw["series"][0]
            and len(resp.raw["series"][0]["values"]) > 0
        ):
            dt_from = resp.raw["series"][0]["values"][0][0]
            self.log.info(f"Newest data for {series} from {dt_from}.")
        else:
            if self.app_config.get("influxdb_reset_db_contents", False):
                self.log.warning(
                    f"Resetting data for {series}, as the reset flag was set",
                )
            else:
                self.log.warning(
                    f"Unable to get last entry timestamp for {series} - resetting.",
                )
            self.db.query(f"DROP SERIES FROM {series}")
        return dt_from, dt_to

    def put_metrics(self, series, metrics):
        def _fields(measurement, factor):
            ret = {
                "raw_consumption": measurement["consumption"],
            }
            if factor not in (None, float(0)) and series == "gas":
                ret["factor"] = factor
            return ret

        def _tags(measurement):
            dt_now = parser.isoparse(measurement["interval_end"])
            return {
                "time_of_day": dt_now.strftime("%H:%M"),
                "date": dt_now.strftime("%d/%m/%Y"),
            }

        measurements = [
            {
                "measurement": series,
                "tags": _tags(measurement),
                "time": measurement["interval_end"],
                "fields": _fields(
                    measurement, self.app_config.get("cron_octopus_gasfac")
                ),
            }
            for measurement in metrics
        ]
        self.db.write_points(measurements)

    def process(self, series):
        self.put_metrics(
            series,
            self.load_series(
                self.uris[series][0]
                % (
                    self.app_config.get(self.uris[series][1]),
                    self.app_config.get(self.uris[series][2]),
                ),
                *self.load_dt(series),
            ),
        )
