from flask import Flask

from RPC.util import Base


class RPCApp(Base, Flask):
    # TODO: Configuration should have SAML or OAuth2/OIDC params for authenticated requests
    # TODO: literally already hate this
    app_config = {
        "debug": False,
        "base_uri": str,
        "auth_aud": str,
        "auth_iss": str,
        "cron_octopus_period": int,
        "cron_octopus_apinum": 1000,
        "cron_octopus_db": str,
        "data_influx_host": str,
        "data_influx_port": 8086,
        "data_influx_tls": False,
        "data_influx_verifytls": False,
        "data_influx_auth": bool,
        "data_influx_user": str,
        "data_influx_pass": str,
        "vnd_octopus_apikey": str,
        "vnd_octopus_elecsn": str,
        "vnd_octopus_gassn": str,
        "vnd_octopus_gasfac": float(0),
        "vnd_octopus_mpan": str,
        "vnd_octopus_mprn": str,
        "vnd_tailscale_apikey": str,
        "vnd_tailscale_tailnet": str,
        "vnd_tailscale_tag": str,
        "vnd_digitalocean_apikey": str,
        "vnd_digitalocean_domain": str,
        "vnd_digitalocean_managed_record": "_tailzone_managed",
    }

    def __init__(self, appid: str):
        super().__init__(None, appid)
