# pylint: disable=missing-module-docstring,missing-function-docstring,invalid-name,line-too-long

import logging
import ipaddress
from flask import Flask, abort, request, jsonify
from werkzeug.exceptions import HTTPException
from frigg.config import ConfigManager
from frigg.push import PushManager
from frigg.auth import AuthManager
from frigg.data import DataManager
from frigg.ddns import CFClient
app = Flask(__name__)
app.logger.setLevel(logging.INFO)

config = ConfigManager(app.logger)
pusher = PushManager(config.get_config('push'), app.logger)
auth = AuthManager(config.get_config('auth'), app.logger)
data = DataManager(config.get_config('data'), app.logger, pusher)
cf = CFClient(config.get_config('ddns'), app.logger, pusher)

def api_return(code: int) -> str:
    desc = {
        200: "OK",
        400: "Wrong Arguments",
        403: "Authentication Failed",
        426: "HTTPS Required",
        500: "Internal Server Error"
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
    if request.url.startswith('http://') and not app.debug:
        return api_return(426)
    hostname = request.args.get('hostname')
    uuid = request.args.get('uuid')
    if hostname is None or uuid is None:
        return api_return(400)
    if not auth.auth(hostname, uuid):
        return api_return(403)
    content = str(request.data, encoding='utf8')
    if content:
        data.write_log(hostname, content, request.remote_addr)
    return api_return(200)


@app.route('/post-beacon', methods=['POST'])
def post_beacon():
    hostname = request.args.get('hostname')
    beacon = request.args.get('beacon')
    meta = str(request.data, encoding='utf8')
    if hostname is None or beacon is None or not data.write_beacon(hostname, beacon, meta, request.remote_addr):
        return api_return(400)
    return api_return(200)


# WIP
@app.route('/post-data', methods=['POST'])
def post_data():
    if request.url.startswith('http://') and not app.debug:
        return api_return(426)
    hostname = request.args.get('hostname')
    uuid = request.args.get('uuid')
    table = request.args.get('table')
    if hostname is None or uuid is None or table is None:
        return api_return(400)
    if not auth.auth(hostname, uuid):
        return api_return(403)
    print(request.form)
    if not data.append_csv(table, request.form):
        return api_return(400)
    return api_return(200)


@app.route('/update-dns', methods=['GET'])
def update_dns():
    if request.url.startswith('http://') and not app.debug:
        return api_return(426)
    hostname = request.args.get('hostname')
    uuid = request.args.get('uuid')
    if hostname is None or uuid is None:
        return api_return(400)
    if not auth.auth(hostname, uuid):
        return api_return(403)
    ip4 = request.args.get('ip4')
    ip6 = request.args.get('ip6')
    if ip4 == "auto":
        ip4 = request.remote_addr
    if ip6 == "auto":
        ip6 = request.remote_addr
    if ip4:
        addr = None
        try:
            addr = ipaddress.ip_address(ip4)
        except ValueError:
            pass
        if not isinstance(addr, ipaddress.IPv4Address):
            app.logger.warning("Invalid IPv4 Address: %s", ip4)
            return api_return(400)
    if ip6:
        addr = None
        try:
            addr = ipaddress.ip_address(ip6)
        except ValueError:
            pass
        if not isinstance(addr, ipaddress.IPv6Address):
            app.logger.warning("Invalid IPv6 Address: %s", ip6)
            return api_return(400)
    if not ip4 and not ip6:
        return api_return(400)
    ret = cf.run(hostname, ip4, ip6)
    if ret:
        return api_return(200)
    return api_return(500)


@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return f"{e.code} {e.name}", e.code
    pusher.push_internal_error(str(e))
    return api_return(500)
