import os, logging


var_dir = os.path.join(os.path.dirname(__file__), 'var')
if not os.path.exists(var_dir):
    var_dir = os.path.join(os.path.dirname(__file__), 'var-example')

def get_var(var_path:str):
    var_full_path = os.path.join(var_dir, var_path)
    if not os.path.exists(var_full_path):
        logging.warning('Request var %s does not exist.' % var_path)
        return None
    with open(var_full_path, 'r') as f:
        return str(f.read()).strip()
