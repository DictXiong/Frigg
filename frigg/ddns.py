# pylint: disable=W,C,R
import time
import cloudflare


class CFClient:
    def __init__(self, config, logger, pusher):
        self.cf = cloudflare.Cloudflare(api_token=config['token'])
        self.logger = logger
        self.pusher = pusher
        try:
            zones = self.cf.zones.list(name=config['zone'])
        except cloudflare.CloudflareError as e:
            self.logger.fatal('error: %s - api call failed' % (e))
        zone = None
        for i in zones:
            if zone is not None:
                self.logger.fatal('error: %s - api call returned >1 zones' % (config['zone']))
            zone = i
        self.zone = zone
        self.zone_name = self.zone.name
        self.zone_id = self.zone.id
        self.logger.info('zone %s found' % (self.zone_name))


    def _aud_record(self, name: str, ip4: str="", ip6: str=""):
        assert name.endswith(self.zone_name)
        for ip_type, ip in [('A', ip4), ('AAAA', ip6)]:
            updated = False
            if not ip:
                updated = True
            dns_records = self.cf.dns.records.list(zone_id=self.zone_id, name=name, type=ip_type, match="all")
            for dns_record in dns_records:
                assert dns_record.type == ip_type and dns_record.name == name
                if updated:
                    self.cf.dns.records.delete(zone_id=self.zone_id, dns_record_id=dns_record.id)
                    self.logger.info('record %s deleted' % (name))
                    continue
                if dns_record.content == ip:
                    self.logger.info('record %s not changed with %s' % (name, ip))
                    updated = True
                    continue
                dns_record_id = dns_record.id
                original_ip = dns_record.content
                dns_record = {
                    'name': name,
                    'type': ip_type,
                    'content': ip,
                    'proxied': False,
                    'comment': f'FRIGG {time.strftime("%Y-%m-%d %H:%M:%S")}'
                }
                dns_record = self.cf.dns.records.update(zone_id=self.zone_id, dns_record_id=dns_record_id, **dns_record)
                self.logger.info('record %s updated to %s' % (name, ip))
                if self.pusher:
                    self.pusher.push_dns_updated(name, ip, original_ip)
                updated = True
            if not updated:
                dns_record = {
                    'name': name,
                    'type': ip_type,
                    'content': ip,
                    'proxied': False,
                    'comment': f'FRIGG {time.strftime("%Y-%m-%d %H:%M:%S")}'
                }
                self.cf.dns.records.create(self.zone_id, **dns_record)
                self.logger.info('record %s created with %s' % (name, ip))
                if self.pusher:
                    self.pusher.push_dns_updated(name, ip)
        return True

    def run(self, name: str, ip4: str, ip6: str):
        assert '.' not in name
        try:
            self._aud_record(f"{name}.0.{self.zone_name}", ip4, ip6)
            self._aud_record(f"{name}.4.{self.zone_name}", ip4=ip4)
            self._aud_record(f"{name}.6.{self.zone_name}", ip6=ip6)
        except cloudflare.CloudFlareError as e:
            self.logger.error('error: %s - api call failed' % (e))
            return False
        return True
