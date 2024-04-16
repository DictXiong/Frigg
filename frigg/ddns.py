# pylint: disable=W,C,R
import CloudFlare
import CloudFlare.exceptions


class CFClient:
    def __init__(self, config, logger, pusher):
        self.cf = CloudFlare.CloudFlare(token=config['token'])
        self.logger = logger
        self.pusher = pusher
        try:
            params = {'name': config['zone']}
            zones = self.cf.zones.get(params=params)
        except CloudFlare.exceptions.CloudFlareError as e:
            self.logger.fatal('error: %s - api call failed' % (e))
        if len(zones) != 1:
            self.logger.fatal('error: %s - api call returned %d zones' % (config['zone'], len(zones)))
        self.zone = zones[0]
        self.zone_name = self.zone['name']
        self.zone_id = self.zone['id']
        self.logger.info('zone %s found' % (self.zone_name))


    def _aud_record(self, name: str, ip4: str="", ip6: str=""):
        assert name.endswith(self.zone_name)
        for ip_type, ip in [('A', ip4), ('AAAA', ip6)]:
            updated = False
            if not ip:
                updated = True
            params = {'name': name, 'match': 'all', 'type': ip_type}
            dns_records = self.cf.zones.dns_records.get(self.zone_id, params=params)
            for dns_record in dns_records:
                assert dns_record['type'] == ip_type and dns_record['name'] == name
                if updated:
                    self.cf.zones.dns_records.delete(self.zone_id, dns_record['id'])
                    self.logger.info('record %s deleted' % (name))
                    continue
                if dns_record['content'] == ip:
                    self.logger.info('record %s not changed with %s' % (name, ip))
                    updated = True
                    continue
                dns_record_id = dns_record['id']
                original_ip = dns_record['content']
                dns_record = {
                    'name': name,
                    'type': ip_type,
                    'content': ip,
                    'proxied': False,
                    'comment': 'Frigg DDNS'
                }
                dns_record = self.cf.zones.dns_records.put(self.zone_id, dns_record_id, data=dns_record)
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
                    'comment': 'Frigg DDNS'
                }
                self.cf.zones.dns_records.post(self.zone_id, data=dns_record)
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
        except CloudFlare.exceptions.CloudFlareError as e:
            self.logger.error('error: %s - api call failed' % (e))
            return False
        return True
