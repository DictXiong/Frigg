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

    def push_dns_updated(self, hostname: str, ip4: str, ip4_before: str, ip6: str, ip6_before: str):
        text = f"## [Frigg.DDNS] {hostname} updated"
        desp = f"**IPv4:** {ip4} (was {ip4_before if ip4 != ip4_before else "the same"})\n**IPv6:** {ip6} (was {ip6_before if ip6 != ip6_before else "the same"})"
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
