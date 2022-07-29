import os, logging


var_dir = os.path.join(os.path.dirname(__file__), 'var')
if not os.path.exists(var_dir):
    var_dir = os.path.join(os.path.dirname(__file__), 'var-example')
def get_var(var_name:str):
    var_path = os.path.join(var_dir, var_name)
    if not os.path.exists(var_path):
        logging.error('Var file %s does not exist.' % var_name)
        return None
    with open(var_path, 'r') as f:
        return str(f.read()).strip()