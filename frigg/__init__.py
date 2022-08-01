from flask import Flask, abort, request
from frigg import data
app = Flask(__name__)


@app.route('/')
def hello_world():
    return '<h1>Welcome to api.beardic.cn</h1>\n'


@app.route('/get-var/<path:var_path>')
def get_var(var_path):
    ret = data.get_var(var_path)
    if ret is not None:
        return ret
    else:
        abort(404)


@app.route('/get-my-ip')
def get_my_ip():
    return request.remote_addr


@app.route('/post-log')
def post_log():
    hostname = request.args.get('hostname')
    uuid = request.args.get('uuid')
    if not data.auth_client(hostname, uuid):
        abort(403)
    return 'OK'


@app.errorhandler(403)
def handle_403(error):
    return '403 forbidden', 403


@app.errorhandler(404)
def handle_404(error):
    return "404 not found", 404
