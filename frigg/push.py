from pypushdeer import PushDeer


class PushManager:
    def __init__(self, config, logger):
        if config["type"] == "pushdeer":
            if "key_file" in config:
                with open(config["key_file"], "r", encoding="utf-8") as f:
                    key = f.read().strip()
            else:
                key = config["key"]
            self.pusher = PushDeer(pushkey=key)
        else:
            raise NotImplementedError(f"pusher {type} not implemented")
        self.type = config["type"]
        self.logger = logger

    def push_beacon(self, hostname: str, beacon: str, meta: str, ip: str):
        text = f"## [Frigg] {beacon} @ {hostname}"
        desp = f"**Reporter:** {ip}"
        if meta:
            desp = f"**Meta:** {meta}\n" + desp
        try:
            if self.type == "pushdeer":
                self.pusher.send_markdown(text, desp=desp)
            else:
                raise NotImplementedError(f"pusher {self.type} not implemented")
        except Exception as e:
            self.logger.error("pusher encountered an error: %s", e)

    def push_dns_updated(self, hostname: str, ip: str, original_ip: str = None):
        text = f"## [Frigg.DDNS] {hostname} updated"
        desp = f"**Content:** {ip}"
        if original_ip:
            desp += f"\n**Was:** {original_ip}"
        try:
            if self.type == "pushdeer":
                self.pusher.send_markdown(text, desp=desp)
            else:
                raise NotImplementedError(f"pusher {self.type} not implemented")
        except Exception as e:
            self.logger.error("pusher encountered an error: %s", e)

    def push_internal_error(self, error: str):
        text = "## [Frigg] Uncaught ERROR"
        desp = f"**Error:** {error}"
        try:
            if self.type == "pushdeer":
                self.pusher.send_markdown(text, desp=desp)
            else:
                raise NotImplementedError(f"pusher {self.type} not implemented")
        except Exception as e:
            self.logger.error("pusher encountered an error: %s", e)
