import os
import yaml


class ConfigManager:
    def __init__(self, config_path, logger) -> None:
        self.logger = logger
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"{config_path} not found")
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        self.config = config

    def get_config(self, key):
        assert key is not None
        return self.config.get(key)
