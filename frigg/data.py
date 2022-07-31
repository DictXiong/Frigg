import os
import yaml
import ipaddress

# global variables
data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
if not os.path.exists(data_dir):
    data_dir = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'data-example')
var_dir = os.path.join(data_dir, 'variables')
auth_config = yaml.full_load(open(os.path.join(data_dir, 'auth.yaml'), 'r'))


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
