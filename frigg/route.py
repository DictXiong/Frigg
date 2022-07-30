from flask import abort
from frigg import app
from frigg import var
import logging

@app.route('/')
def hello_world():
    return '<h1>Welcome to api.beardic.cn</h1>\n'


@app.route('/get-var/<path:var_path>')
def get_var(var_path):
    logging.info(f"Request var: {var_path}")
    ret = var.get_var(var_path)
    if ret is not None:
        return ret
    else:
        abort(404)


@app.errorhandler(404)
def handle_404(error):
    return "404 not found", 404
