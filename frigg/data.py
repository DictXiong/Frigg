"""
This module manages the client's data. All data is stored in the data directory.
"""
# pylint: disable=line-too-long,invalid-name,redefined-outer-name,missing-function-docstring
import os
import ipaddress
import logging
import logging.handlers
import csv
from frigg.push import PushManager


class DataManager:
    def __init__(self, config, logger, pusher) -> None:
        self.logger = logger
        self.pusher = pusher
        self.config = config
        # data dir
        data_dir = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'data')
        if not os.path.exists(data_dir):
            raise FileNotFoundError('data directory not found')
        self.data_dir = data_dir
        # var dir
        var_dir = os.path.join(data_dir, 'variables')
        if not os.path.exists(var_dir):
            os.makedirs(var_dir)
        self.var_dir = var_dir
        # csv dir
        csv_dir = os.path.join(data_dir, 'csv')
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        self.csv_dir = csv_dir
        # client logger
        client_log_dir = os.path.join(data_dir, 'log')
        if not os.path.exists(client_log_dir):
            os.makedirs(client_log_dir)
        client_log_path = os.path.join(client_log_dir, 'client.log')
        client_logger = logging.getLogger('post-log')
        client_logger.setLevel(logging.DEBUG)
        file_handler = logging.handlers.RotatingFileHandler(
            client_log_path, backupCount=10, maxBytes=10*1024*1024, encoding='utf8')
        file_handler.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '[%(asctime)s][client]%(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        client_logger.addHandler(file_handler)
        client_logger.addHandler(console_handler)
        client_logger.info(' post-log logger initialized')
        self.client_logger = client_logger
        # beacon logger
        beacon_log_path = os.path.join(data_dir, 'log', 'beacon.log')
        beacon_logger = logging.getLogger('post-beacon')
        beacon_logger.setLevel(logging.DEBUG)
        file_handler = logging.handlers.RotatingFileHandler(
            beacon_log_path, backupCount=5, maxBytes=5*1024*1024, encoding='utf8')
        file_handler.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '[%(asctime)s][beacon]%(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        beacon_logger.addHandler(file_handler)
        beacon_logger.addHandler(console_handler)
        beacon_logger.info(' beacon logger initialized')
        self.beacon_logger = beacon_logger

    def get_var(self, var_path: str):
        var_full_path = os.path.realpath(os.path.join(self.var_dir, var_path))
        if not var_full_path.startswith(self.var_dir) or not os.path.exists(var_full_path):
            return None
        with open(var_full_path, 'r', encoding="utf8") as f:
            return str(f.read()).strip()

    def write_log(self, hostname: str, content: str, ip: str):
        self.client_logger.info("[%s]::%s (%s)", hostname, content, ip)
        return True

    def write_beacon(self, hostname: str, beacon: str, meta: str, ip: str):
        if beacon not in self.config['beacon']['types'] or len(hostname) > 64:
            return False
        if meta:
            if len(meta) > 512:
                return False
            self.beacon_logger.info(
                "[%s]::%s \"%s\" (%s)", hostname, beacon, meta, ip)
        else:
            self.beacon_logger.info("[%s]::%s (%s)", hostname, beacon, ip)
        if self.pusher and beacon in self.config['beacon']['push']:
            self.pusher.push_beacon(
                hostname=hostname, beacon=beacon, meta=meta, ip=ip)
        return True

    # WIP
    def append_csv(self, csv_name: str, data: dict):
        csv_full_path = os.path.realpath(
            os.path.join(self.csv_dir, csv_name + '.csv'))
        if not os.path.exists(csv_full_path) or not csv_full_path.startswith(self.csv_dir):
            return False
        field_names = []
        with open(csv_full_path, 'r', encoding='utf8') as f:
            field_names = csv.DictReader(f).fieldnames
        with open(csv_full_path, 'a', encoding='utf8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=field_names)
            try:
                dict_writer.writerow(data)
            except ValueError:
                return False
        return True
