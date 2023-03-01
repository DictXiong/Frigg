import os
import yaml

class ConfigManager:
    def __init__(self, logger) -> None:
        self.logger = logger
        config_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'config.yaml')
        if not os.path.exists(config_path):
            raise FileNotFoundError('config.yaml not found')
        with open(config_path, 'r', encoding='utf8') as f:
            config = yaml.full_load(f)
        self.config = config
    
    def get_config(self, key):
        assert key is not None and key in self.config
        return self.config[key]