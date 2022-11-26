# pylint: disable=missing-module-docstring,missing-function-docstring,invalid-name,line-too-long

from flask import Flask, abort, request, jsonify
from werkzeug.exceptions import HTTPException
from frigg import data
app = Flask(__name__)


def api_return(code: int) -> str:
    desc = {
        200: "OK",
        400: "Wrong Arguments",
        403: "Authentication Failed",
    }
    return jsonify({"status": code, "desc": desc[code]}), 200


@app.route('/')
def hello_world():
    return '<h1>Welcome to api.beardic.cn</h1>', 200


@app.route('/get-var/<path:var_path>')
def get_var(var_path):
    ret = data.get_var(var_path)
    if ret is not None:
        return ret
    abort(404)


@app.route('/get-my-ip')
def get_my_ip():
    return request.remote_addr


@app.route('/post-log', methods=['POST'])
def post_log():
    hostname = request.args.get('hostname')
    uuid = request.args.get('uuid')
    if hostname is None or uuid is None:
        return api_return(400)
    if not data.auth_client(hostname, uuid):
        return api_return(403)
    content = str(request.data, encoding='utf8')
    if content:
        data.write_log(hostname, content, request.remote_addr)
    return api_return(200)


@app.route('/post-beacon', methods=['POST'])
def post_beacon():
    hostname = request.args.get('hostname')
    beacon = request.args.get('beacon')
    if hostname is None or beacon is None or not data.write_beacon(hostname, beacon, request.remote_addr):
        return api_return(400)
    return api_return(200)


@app.route('/post-data', methods=['POST'])
def post_data():
    hostname = request.args.get('hostname')
    uuid = request.args.get('uuid')
    table = request.args.get('table')
    if hostname is None or uuid is None or table is None:
        return api_return(400)
    if not data.auth_client(hostname, uuid):
        return api_return(403)
    print(request.form)
    if not data.append_csv(table, request.form):
        return api_return(400)
    return api_return(200)


@app.errorhandler(HTTPException)
def handle_exception(e):
    return f"{e.code} {e.name}", e.code
