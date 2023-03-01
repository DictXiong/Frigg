from pypushdeer import PushDeer


class PushManager:
    def __init__(self, config, logger):
        if config['type'] == "pushdeer":
            self.pusher = PushDeer(pushkey=config['key'])
        else:
            raise NotImplementedError(f"pusher {type} not implemented")
        self.type = config['type']
        self.logger = logger
        self.enable = config['enable']

    def push_beacon(self, hostname: str, beacon: str, meta: str, ip: str):
        if not self.enable:
            return
        text = f"## [Frigg] {hostname}::{beacon}"
        desp = f"**IP:** {ip}"
        if meta:
            desp = f"**Meta:** {meta}; \n" + desp
        try:
            if self.type == "pushdeer":
                self.pusher.send_markdown(text, desp=desp)
            else:
                raise NotImplementedError(
                    f"pusher {self.type} not implemented")
        except Exception as e:
            self.logger.error(f"pusher encountered an error: {e}")

    def push_dns_updated(self, hostname: str, ip: str, original_ip: str = None):
        if not self.enable:
            return
        text = f"## [Frigg.DDNS] {hostname} updated"
        desp = f"**IP:** {ip}"
        if original_ip:
            desp += f"; \n**Original IP:** {original_ip}"
        try:
            if self.type == "pushdeer":
                self.pusher.send_markdown(text, desp=desp)
            else:
                raise NotImplementedError(
                    f"pusher {self.type} not implemented")
        except Exception as e:
            self.logger.error(f"pusher encountered an error: {e}")
