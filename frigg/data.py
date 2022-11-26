"""
This module manages the client's data. All data is stored in the data directory.
"""
# pylint: disable=line-too-long,invalid-name,redefined-outer-name,missing-function-docstring
import os
import ipaddress
import logging
import logging.handlers
import csv
import yaml


def init_data_dir():
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
    if not os.path.exists(data_dir):
        data_dir = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'data-example')
    return data_dir


def init_var_dir(data_dir):
    # var dir
    var_dir = os.path.join(data_dir, 'variables')
    if not os.path.exists(var_dir):
        os.makedirs(var_dir)
    return var_dir


def init_csv_dir(data_dir):
    csv_dir = os.path.join(data_dir, 'csv')
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    return csv_dir


def init_config(data_dir):
    config_path = os.path.join(data_dir, 'config.yaml')
    if not os.path.exists(config_path):
        raise FileNotFoundError('config.yaml not found')
    with open(config_path, 'r', encoding='utf8') as f:
        config = yaml.full_load(f)
    return config


def init_client_logger(data_dir):
    # client log dir
    client_log_dir = os.path.join(data_dir, 'log')
    if not os.path.exists(client_log_dir):
        os.makedirs(client_log_dir)
    client_log_path = os.path.join(client_log_dir, 'client.log')
    # client_logger
    client_logger = logging.getLogger('post-log')
    client_logger.setLevel(logging.DEBUG)
    file_handler = logging.handlers.RotatingFileHandler(client_log_path, backupCount=10, maxBytes=10*1024*1024, encoding='utf8')
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
    return client_logger


def init_beacon_recorder(data_dir):
    # client log dir
    client_log_dir = os.path.join(data_dir, 'log')
    if not os.path.exists(client_log_dir):
        os.makedirs(client_log_dir)
    client_log_path = os.path.join(client_log_dir, 'beacon.log')
    # beacon_logger
    beacon_logger = logging.getLogger('post-beacon')
    beacon_logger.setLevel(logging.DEBUG)
    file_handler = logging.handlers.RotatingFileHandler(client_log_path, backupCount=5, maxBytes=5*1024*1024, encoding='utf8')
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
    return beacon_logger


data_dir = init_data_dir()
var_dir = init_var_dir(data_dir)
csv_dir = init_csv_dir(data_dir)
config = init_config(data_dir)
client_logger = init_client_logger(data_dir)
beacon_logger = init_beacon_recorder(data_dir)


def get_var(var_path: str):
    var_full_path = os.path.realpath(os.path.join(var_dir, var_path))
    if not var_full_path.startswith(var_dir) or not os.path.exists(var_full_path):
        return None
    with open(var_full_path, 'r', encoding="utf8") as f:
        return str(f.read()).strip()


def auth_client(hostname: str, uuid: str):
    """
    auth the client by hostname and uuid.
    this can accept None-s normally
    """
    return bool(hostname in config['auth']['clients'] and uuid == config['auth']['clients'][hostname]['uuid'])


def auth_ip(hostname: str, ip: str):
    """
    verify the ip address
    """
    ip_network = config['auth']['clients'][hostname]['ip']
    ip = ipaddress.ip_address(ip)
    if isinstance(ip_network, str):
        ip_network = [ipaddress.ip_network(ip_network)]
    elif isinstance(ip_network, list):
        ip_network = [ipaddress.ip_network(i) for i in ip_network]
    elif ip_network is None:
        return True
    else:
        raise TypeError('In config.yaml/auth/clients, ip must be str, list or None')
    for i in ip_network:
        if ip in i:
            return True
    return False


def write_log(hostname: str, content: str, ip: str):
    client_logger.info("[%s]::%s::[%s]", hostname, content, ip)
    return True


def write_beacon(hostname: str, beacon: str, ip: str):
    if beacon not in config['beacon']['types']:
        return False
    beacon_logger.info("[%s]::%s::[%s]", hostname, beacon, ip)
    return True


def append_csv(csv_name: str, data: dict):
    csv_full_path = os.path.realpath(os.path.join(csv_dir, csv_name + '.csv'))
    if not os.path.exists(csv_full_path) or not csv_full_path.startswith(csv_dir):
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
