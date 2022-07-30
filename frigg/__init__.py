from flask import Flask, abort, request
from frigg import var
app = Flask(__name__)


@app.route('/')
def hello_world():
    return '<h1>Welcome to api.beardic.cn</h1>\n'


@app.route('/get-var/<path:var_path>')
def get_var(var_path):
    ret = var.get_var(var_path)
    if ret is not None:
        return ret
    else:
        abort(404)


@app.route('/get-my-ip')
def get_my_ip():
    return request.remote_addr


@app.errorhandler(404)
def handle_404(error):
    return "404 not found", 404
