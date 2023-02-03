from asyncio import run as wait

from digitalocean import Domain as DOdomain
from tailscale import Tailscale

from RPC.util.helpers import Configurable


class Tailzone(Configurable):
    app_config = {
        "debug": False,
        "base_uri": str,
        "vnd_tailscale_apikey": str,
        "vnd_tailscale_tailnet": str,
        "vnd_tailscale_tag": str,
        "vnd_digitalocean_apikey": str,
        "vnd_digitalocean_domain": str,
        "vnd_digitalocean_managed_record": "_tailzone_managed",
    }

    async def get_devices(self):
        network = Tailscale(
            api_key=self.app_config.get("vnd_tailscale_apikey"),
            tailnet=self.app_config.get("vnd_tailscale_tailnet"),
        )

        # TODO: external devices do not have tags,
        #       but maybe they should be published under HOSTNAME.external?
        # TODO: what if a host doesn't have an ipv6 or ipv4 address? how do we know?
        #       v4 addresses will always(?) start with 100., v6 will always(?) start with fd7a:
        devices = await network.devices()
        devices = [
            {
                "host": devices[device].name.split(".")[0].lower(),
                "a4": devices[device].addresses[0],
                "a6": devices[device].addresses[1],
                "extern": devices[device].is_external,
                "tags": devices[device].tags
                if devices[device].tags is not None
                else [],
            }
            for device in devices
        ]
        await network.session.close()
        await network.close()
        return devices

    def main(self, *args, **kwargs):
        results = {
            "mode": "periodic"
            if not self.app_config.get("tailzone_destroy_all_managed_records", False)
            else "destroy",
            "poll_stats": {
                "count_dns_records": 0,
                "count_tailscale_devices": 0,
                "count_existing_managed": 0,
                "count_existing_orphaned": 0,
                "count_existing_pending": 0,
                "count_removable_managed": 0,
            },
            "outcomes": {
                "created": {
                    "a": 0,
                    "aaaa": 0,
                    "txt": 0,
                },
                "destroyed": {
                    "a": 0,
                    "aaaa": 0,
                    "txt": 0,
                },
            },
        }

        devices = wait(self.get_devices())
        results["poll_stats"]["count_tailscale_devices"] = len(devices)

        domain = DOdomain(
            token=self.app_config.get("vnd_digitalocean_apikey"),
            name=self.app_config.get("vnd_digitalocean_domain"),
        )
        records = domain.get_records()
        results["poll_stats"]["count_dns_records"] = len(records)

        # Collect all currently-managed records, if any
        # Managed records are stored by name in individual text records
        #  under _tailzone_managed.$DOMAIN
        managed = [
            record.data.lower()
            for record in records
            if record.name == self.app_config.get("vnd_digitalocean_managed_record")
            and record.type == "TXT"
        ]
        results["poll_stats"]["count_existing_managed"] = len(managed)

        pending = [
            host
            for host in devices
            if f"tag:{self.app_config.get('vnd_tailscale_tag')}" in host["tags"]
            and host["host"] not in managed
        ]
        results["poll_stats"]["count_existing_pending"] = len(pending)

        removable = [
            host["host"]
            for host in devices
            if f"tag:{self.app_config.get('vnd_tailscale_tag')}" not in host["tags"]
            and host["host"] in managed
        ]
        results["poll_stats"]["count_removable_managed"] = len(removable)

        orphaned = [
            name for name in managed if name not in [host["host"] for host in devices]
        ]
        results["poll_stats"]["count_existing_orphaned"] = len(orphaned)

        if self.app_config.get("tailzone_destroy_all_managed_records", False):
            removable = [
                *[host["host"] for host in pending],
                *managed,
                *removable,
            ]
            managed = []
            pending = []

        changeset = {
            "destroy": [
                {
                    "name": record.name.lower(),
                    "data": record.data.lower(),
                    "type": record.type,
                    "result": record.destroy(),
                }
                for record in records
                if (
                    record.name.lower() in [*orphaned, *removable]
                    and record.type in ("A", "AAAA")
                )
                or (
                    record.name
                    == self.app_config.get("vnd_digitalocean_managed_record")
                    and record.type == "TXT"
                    and record.data.lower() in [*orphaned, *removable]
                )
            ],
            "create_a": [
                {
                    "name": host["host"],
                    "result": domain.create_new_domain_record(
                        type="A", name=host["host"], data=host["a4"]
                    ),
                }
                for host in pending
            ],
            "create_aaaa": [
                {
                    "name": host["host"],
                    "result": domain.create_new_domain_record(
                        type="AAAA", name=host["host"], data=host["a6"]
                    ),
                }
                for host in pending
            ],
            "create_txt": [
                {
                    "name": host["host"],
                    "result": domain.create_new_domain_record(
                        type="TXT",
                        name=self.conf.get("vnd_digitalocean_managed_record"),
                        data=host["host"],
                    ),
                }
                for host in pending
            ],
        }

        for rrtype in ("a", "aaaa", "txt"):
            results["outcomes"]["created"][rrtype] = len(changeset[f"create_{rrtype}"])
            results["outcomes"]["destroyed"][rrtype] = len(
                [res for res in changeset["destroy"] if res["type"].lower() == rrtype]
            )

        return
