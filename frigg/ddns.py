# pylint: disable=W,C,R
import time
import cloudflare


class CFClient:
    def __init__(self, config, logger, pusher):
        if "token_file" in config:
            with open(config["token_file"], "r", encoding="utf-8") as f:
                token = f.read().strip()
        else:
            token = config["token"]
        self.cf = cloudflare.Cloudflare(api_token=token)
        self.logger = logger
        self.pusher = pusher
        try:
            zones = self.cf.zones.list(name=config["zone"])
        except cloudflare.APIError as e:
            self.logger.fatal("error: %s - api call failed", e)
            exit(-1)
        zone = None
        for i in zones:
            if zone is not None:
                self.logger.fatal(
                    "error: %s - api call returned >1 zones", config["zone"]
                )
                exit(-1)
            zone = i
        self.zone = zone
        self.zone_name = self.zone.name
        self.zone_id = self.zone.id
        self.logger.info("zone %s found", self.zone_name)

    def _aud_record(self, name: str, ip4: str=None, ip6: str=None, push=False):
        assert name.endswith(self.zone_name)
        ip4_before = None
        ip6_before = None
        for ip_type, ip in [("A", ip4), ("AAAA", ip6)]:
            updated = False
            if not ip:
                updated = True
            dns_records = self.cf.dns.records.list(
                zone_id=self.zone_id, name=name, type=ip_type, match="all"
            )
            for dns_record in dns_records:
                assert dns_record.type == ip_type and dns_record.name == name
                if ip_type == "A":
                    ip4_before = dns_record.content
                else:
                    ip6_before = dns_record.content
                if updated:
                    self.cf.dns.records.delete(
                        zone_id=self.zone_id, dns_record_id=dns_record.id
                    )
                    self.logger.info("record %s deleted", name)
                    continue
                if dns_record.content == ip:
                    self.logger.info("record %s not changed with %s", name, ip)
                    updated = True
                    continue
                dns_record = {
                    "dns_record_id": dns_record.id,
                    "name": name,
                    "type": ip_type,
                    "content": ip,
                    "proxied": False,
                    "comment": f'FRIGG {time.strftime("%Y-%m-%d %H:%M:%S")}',
                }
                dns_record = self.cf.dns.records.update(
                    zone_id=self.zone_id, **dns_record
                )
                self.logger.info("record %s updated to %s", name, ip)
                updated = True
            if not updated:
                dns_record = {
                    "name": name,
                    "type": ip_type,
                    "content": ip,
                    "proxied": False,
                    "comment": f'FRIGG {time.strftime("%Y-%m-%d %H:%M:%S")}',
                }
                self.cf.dns.records.create(zone_id=self.zone_id, **dns_record)
                self.logger.info("record %s created with %s", name, ip)
        if (ip4 != ip4_before or ip6 != ip6_before) and push and self.pusher:
            self.pusher.push_dns_updated(name.split(".")[0], ip4=ip4, ip4_before=ip4_before, ip6=ip6, ip6_before=ip6_before)
        return True

    def run(self, name: str, ip4: str, ip6: str):
        assert "." not in name
        if not ip4: ip4 = None
        if not ip6: ip6 = None
        try:
            self._aud_record(f"{name}.0.{self.zone_name}", ip4, ip6, push=True)
            self._aud_record(f"{name}.4.{self.zone_name}", ip4=ip4)
            self._aud_record(f"{name}.6.{self.zone_name}", ip6=ip6)
        except cloudflare.APIError as e:
            self.logger.error("error: %s - api call failed", e)
            return False
        return True
