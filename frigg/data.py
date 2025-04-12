"""
This module manages the client's data. All data is stored in the data directory.
"""

# pylint: disable=line-too-long,invalid-name,redefined-outer-name,missing-function-docstring
import logging
import logging.handlers


class DataManager:
    def __init__(self, config, logger, pusher) -> None:
        self.logger = logger
        self.pusher = pusher
        self.config = config

        # beacon logger
        beacon_logger = logging.getLogger("beacon")
        beacon_logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(asctime)s][beacon]%(message)s")
        console_handler.setFormatter(formatter)
        beacon_logger.addHandler(console_handler)
        self.beacon_logger = beacon_logger

    def write_beacon(self, hostname: str, beacon: str, meta: str, ip: str):
        if beacon not in self.config["beacon"] or len(hostname) > 32:
            return False
        if meta:
            if len(meta) > 512:
                return False
            self.beacon_logger.info('[%s]::%s "%s" (%s)', hostname, beacon, meta, ip)
        else:
            self.beacon_logger.info("[%s]::%s (%s)", hostname, beacon, ip)
        if self.pusher and self.config["beacon"][beacon]:
            self.pusher.push_beacon(hostname=hostname, beacon=beacon, meta=meta, ip=ip)
        return True
