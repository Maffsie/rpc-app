from asyncio import run as wait

from digitalocean import Domain as DOdomain
from tailscale import Tailscale

from flask import current_app as rpc

from RPC import RPCApp
from RPC.helper import Configurable
from RPC.models import TailscaleHost

rpc: RPCApp


class Tailzone(Configurable):
    app_config = {
        "tailscale_apikey": str,
        "tailzone_ts_net": str,
        "tailzone_ts_tag": str,
        "digitalocean_apikey": str,
        "tailzone_do_domain": str,
        "tailzone_do_record": "_tailzone_managed",
    }

    async def get_devices(self) -> list[TailscaleHost]:
        network = Tailscale(
            api_key=self.app_config.get("tailscale_apikey"),
            tailnet=self.app_config.get("tailzone_ts_net"),
        )

        # TODO: external devices do not have tags,
        #       but maybe they should be published under HOSTNAME.external?
        # TODO: what if a host doesn't have an ipv6 or ipv4 address? how do we know?
        #       v4 addresses will always(?) start with 100., v6 will always(?) start with fd7a:
        devices = await network.devices()
        devices = [
            TailscaleHost(hostname=devices[device].name.split(".")[0].lower(),
                          extern=devices[device].is_external,
                          _tags=devices[device].tags or [],
                          _publish_tag=self.app_config.get("tailzone_ts_tag"),
                          a4=devices[device].addresses[0],
                          a6=devices[device].addresses[1])
            for device in devices
        ]
        await network.session.close()
        await network.close()
        return devices

    def tailzone(self, *args, **kwargs):
        rpc.log.info("tailzone start", step="begin")
        devices = wait(self.get_devices())
        rpc.log.info("got device list", step="get_devices", device_count=len(devices))

        domain = DOdomain(
            token=self.app_config.get("digitalocean_apikey"),
            name=self.app_config.get("tailzone_do_domain"),
        )
        records = domain.get_records()
        rpc.log.info("got DO domain records", step="get_records",
                     record_count=len(records), domain=domain.name)

        # Collect all currently-managed records, if any
        # Managed records are stored by name in individual text records
        #  under _tailzone_managed.$DOMAIN
        managed = [
            record.data.lower()
            for record in records
            if record.name == self.app_config.get("tailzone_do_record")
            and record.type == "TXT"
        ]

        pending = [
            host
            for host in devices
            if host.publish
            and host.hostname not in managed
        ]

        removable = [
            host.hostname
            for host in devices
            if host in managed
            and not host.publish
        ]

        orphaned = [
            name
            for name in managed
            if name not in [
                host.hostname
                for host in devices
            ]
        ]

        rpc.log.info("sorted into lists", step="list_sort",
                     managed=len(managed), pending=len(pending),
                     removable=len(removable), orphaned=len(orphaned))

        if self.app_config.get("tailzone_destroy_all_managed_records", False):
            removable = [
                *[host.hostname for host in pending],
                *managed,
                *removable,
            ]
            managed = []
            pending = []
            rpc.log.warn("will destroy all tailzone-managed records", step="destroy",
                         to_destroy=len(removable))

        # To batch up creation and destruction in a single listcomp,
        #  abuse tuples :)
        destroyed = [
            (record.name, record.destroy())[0]
            for record in records
            if (record.name.lower() in [*orphaned, *removable]
                and record.type in ("A", "AAAA"))
            or (record.type == "TXT"
                and record.name == self.app_config.get("tailzone_do_record")
                and record.data.lower() in [*orphaned, *removable])
        ]
        rpc.log.info("destroyed records", step="destroy_records",
                     destroyed=len(destroyed))
        created = [(
            host.hostname,
            domain.create_new_domain_record(
                type="A", name=host.hostname, data=host.a4),
            domain.create_new_domain_record(
                type="AAAA", name=host.hostname, data=host.a6),
            domain.create_new_domain_record(
                type="TXT", name=self.app_config.get("tailzone_do_record"), data=host.hostname)
            )[0]
            for host in pending
        ]
        rpc.log.info("created records", step="create_records",
                     created=len(created))

        rpc.log.info("tailzone finished", step="end", success=True)
        return


p_cls = Tailzone
