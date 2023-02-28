from pypushdeer import PushDeer


class PushManager:
    def __init__(self, type, key, logger):
        if type == "pushdeer":
            self.pusher = PushDeer(pushkey=key)
        else:
            raise NotImplementedError(f"pusher {type} not implemented")
        self.type = type
        self.logger = logger

    def push_beacon(self, hostname: str, beacon: str, meta: str, ip: str):
        text = f"[Frigg] {hostname}::{beacon}"
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

    def push_dns_updated(self, hostname: str, ip: str):
        text = f"[Frigg] {hostname} DNS updated to {ip}"
        try:
            if self.type == "pushdeer":
                self.pusher.send_markdown(text)
            else:
                raise NotImplementedError(
                    f"pusher {self.type} not implemented")
        except Exception as e:
            self.logger.error(f"pusher encountered an error: {e}")
