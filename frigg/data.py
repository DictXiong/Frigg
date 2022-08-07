import os
import yaml
import ipaddress
import logging
import logging.handlers

# global variables
global var_dir, auth_config, client_logger
def initialize():
    global var_dir, auth_config, client_logger
    # data dir
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
    if not os.path.exists(data_dir):
        data_dir = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'data-example')
    # var dir
    var_dir = os.path.join(data_dir, 'variables')
    if not os.path.exists(var_dir):
        os.makedirs(var_dir)
    # auth config
    auth_config_path = os.path.join(data_dir, 'auth.yaml')
    if not os.path.exists(auth_config_path):
        with open(auth_config_path, 'w') as f:
            f.write("clients: ~")
    with open(auth_config_path, 'r') as f:
        auth_config = yaml.full_load(f)
    # client log dir
    client_log_dir = os.path.join(data_dir, 'client-log')
    if not os.path.exists(client_log_dir):
        os.makedirs(client_log_dir)
    client_log_path = os.path.join(client_log_dir, 'client.log')
    client_logger = logging.getLogger('client-log')
    client_logger.setLevel(logging.DEBUG)
    file_handler = logging.handlers.TimedRotatingFileHandler(client_log_path, when="W0", backupCount=10)
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(asctime)s][%(filename)s:%(lineno)d]%(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    client_logger.addHandler(file_handler)
    client_logger.addHandler(console_handler)
    client_logger.info(' client logger initialized')

initialize()

def get_var(var_path: str):
    var_full_path = os.path.realpath(os.path.join(var_dir, var_path))
    if not var_full_path.startswith(var_dir) or not os.path.exists(var_full_path):
        return None
    with open(var_full_path, 'r') as f:
        return str(f.read()).strip()

# auth the client by hostname and uuid
# this can accept None-s normally
def auth_client(hostname: str, uuid: str):
    if hostname in auth_config['clients'] and uuid == auth_config['clients'][hostname]['uuid']:
        return True
    else:
        return False

# verify the ip address
def auth_ip(hostname: str, ip: str):
    ip_network = auth_config['clients'][hostname]['ip']
    ip = ipaddress.ip_address(ip)
    if type(ip_network) is str:
        ip_network = [ipaddress.ip_network(ip_network)]
    elif type(ip_network) is list:
        ip_network = [ipaddress.ip_network(i) for i in ip_network]
    elif type(ip_network) is None:
        return True
    else:
        raise TypeError('In auth.yaml, ip must be str, list or None')
    for i in ip_network:
        if ip in i:
            return True
    return False

def write_log(hostname: str, content: str):
    client_logger.info(f"<{hostname}> {content}")
    return True