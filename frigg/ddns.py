# pylint: disable=W,C,R
import CloudFlare


class DDNS:
    def __init__(self, zone: str, token: str, logger, pusher=None):
        self.cf = CloudFlare.CloudFlare(token=token)
        self.logger = logger
        self.pusher = pusher
        try:
            params = {'name': zone}
            zones = self.cf.zones.get(params=params)
        except Exception as e:
            self.logger.fatal('Error: %s - api call failed' % (e))
        if len(zones) != 1:
            self.logger.fatal('Error: %s - api call returned %d zones' % (zone, len(zones)))
        self.zone = zones[0]
        self.zone_name = self.zone['name']
        self.zone_id = self.zone['id']
        self.logger.info('Zone %s found' % (self.zone_name))


    def add_or_update_record(self, name: str, ip4: str, ip6: str):
        assert name.endswith(self.zone_name)
        ips = {'A': ip4, 'AAAA': ip6}
        for ip_type, ip in ips.items():
            if not ip:
                continue
            try:
                params = {'name': name, 'match': 'all', 'type': ip_type}
                dns_records = self.cf.zones.dns_records.get(self.zone_id, params=params)
            except Exception as e:
                self.logger.error('Error: %s - api call failed' % (e))
                return False
            updated = False
            for dns_record in dns_records:
                if dns_record['type'] != ip_type:
                    continue
                if dns_record['content'] == ip:
                    assert dns_record['name'] == name
                    self.logger.info('Record %s not changed with %s' % (name, ip))
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
                try:
                    dns_record = self.cf.zones.dns_records.put(self.zone_id, dns_record_id, data=dns_record)
                except Exception as e:
                    self.logger.error('Error: %s - api call failed' % (e))
                    return False
                self.logger.info('Record %s updated to %s' % (name, ip))
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
                try:
                    self.cf.zones.dns_records.post(self.zone_id, data=dns_record)
                except Exception as e:
                    self.logger.error('Error: %s - api call failed' % (e))
                    return False
                self.logger.info('Record %s created with %s' % (name, ip))
                if self.pusher:
                    self.pusher.push_dns_updated(name, ip)
        return True
