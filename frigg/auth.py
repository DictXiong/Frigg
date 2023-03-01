import ipaddress

class AuthManager:
    def __init__(self, config, logger) -> None:
        self.config = config
        self.logger = logger

    def auth(self, hostname, uuid):
        if hostname is None or uuid is None:
            return False
        if hostname not in self.config['clients']:
            return False
        if uuid != self.config['clients'][hostname]['uuid']:
            return False
        self.logger.info('auth success: %s', hostname)
        return True

    # this is useless
    # def auth_ip(self, hostname: str, ip: str):
    #     """
    #     verify the ip address
    #     """
    #     ip_network = self.config['clients'][hostname]['ip']
    #     ip = ipaddress.ip_address(ip)
    #     if isinstance(ip_network, str):
    #         ip_network = [ipaddress.ip_network(ip_network)]
    #     elif isinstance(ip_network, list):
    #         ip_network = [ipaddress.ip_network(i) for i in ip_network]
    #     elif ip_network is None:
    #         return True
    #     else:
    #         raise TypeError(
    #             'In config.yaml/auth/clients, ip must be str, list or None')
    #     for i in ip_network:
    #         if ip in i:
    #             return True
    #     return False
