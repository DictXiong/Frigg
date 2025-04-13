# pylint: disable=missing-module-docstring,missing-function-docstring,invalid-name,line-too-long

import re
import logging
import argparse
import ipaddress
from flask import Flask, abort, request, jsonify
from werkzeug.exceptions import HTTPException
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .config import ConfigManager
from .push import PushManager
from .data import DataManager
from .ddns import CFClient
from .db import DBManager

parser = argparse.ArgumentParser()
parser.add_argument(
    "-c", "--config", default="frigg.yaml", help="Path to the configuration file"
)
parser.add_argument("-v", "--verbose", help="Show more log", action="store_true")
args, _ = parser.parse_known_args()

app = Flask(__name__)
if args.verbose:
    app.logger.setLevel(logging.DEBUG)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=['600 per 10 minutes'])


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[32;20m"
    reset = "\x1b[0m"
    template = "%(levelname)s in %(filename)s: %(message)s"

    FORMATS = {
        logging.DEBUG: grey + template + reset,
        logging.INFO: green + template + reset,
        logging.WARNING: yellow + template + reset,
        logging.ERROR: red + template + reset,
        logging.CRITICAL: bold_red + template + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


log_level = logging.DEBUG if args.verbose else logging.INFO
logger = logging.getLogger("frigg")
logger.setLevel(log_level)
ch = logging.StreamHandler()
ch.setLevel(log_level)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

config = ConfigManager(args.config, logger)
pusher = PushManager(config.get_config("push"), logger)
data = DataManager(config.get_config("data"), logger, pusher)
db = DBManager(config.get_config("db"), logger)
cf = CFClient(config.get_config("ddns"), logger, pusher)


def api_return(code: int, desc=None) -> str:
    DESC = {
        200: "OK",
        400: "Wrong Arguments",
        403: "Authentication Failed",
        426: "HTTPS Required",
        500: "Internal Server Error",
    }
    return jsonify({"status": code, "desc": DESC[code] if desc is None else desc}), 200


def invalid_var_path(s: str):
    return re.fullmatch(r"[a-z][-a-z/]*", s) is None


def invalid_hostname(s: str):
    return re.fullmatch(r"[a-z][-a-z0-9_]*", s) is None


def invalid_uuid(s: str):
    return (
        re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", s)
        is None
    )


def invalid_beacon(s: str):
    return re.fullmatch(r"[a-z][-a-z.]*", s) is None


@app.route("/")
def hello_world():
    return "<h1>Welcome to api.beardic.cn</h1>", 200


@app.route("/get-var/<path:var_path>")
@app.route("/var/<path:var_path>")
def get_var(var_path):
    if invalid_var_path(var_path):
        abort(400)
    ret = db.get_var(var_path)
    if ret is not None:
        return ret
    abort(404)


@app.route("/get-my-ip")
@app.route("/ip")
def get_my_ip():
    return request.remote_addr


@limiter.limit("60 per 10 minutes")
@app.route("/post-beacon", methods=["POST"])
@app.route("/beacon", methods=["POST"])
def post_beacon():
    hostname = request.args.get("hostname")
    beacon = request.args.get("beacon")
    meta = str(request.data, encoding="utf8")
    if (
        invalid_hostname(hostname)
        or invalid_beacon(beacon)
        or not data.write_beacon(hostname, beacon, meta, request.remote_addr)
    ):
        return api_return(400)
    return api_return(200)


@app.route("/update-dns", methods=["GET"])
@app.route("/ddns", methods=["GET"])
def update_dns():
    if request.url.startswith("http://") and not app.debug:
        return api_return(426)
    hostname = request.args.get("hostname")
    uuid = request.args.get("uuid")
    if invalid_hostname(hostname) or invalid_uuid(uuid):
        return api_return(400)
    if not db.auth_host(hostname, uuid):
        return api_return(403)
    ip4 = request.args.get("ip4")
    ip6 = request.args.get("ip6")
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
            logger.warning("Invalid IPv4 Address: %s", ip4)
            return api_return(400)
    if ip6:
        addr = None
        try:
            addr = ipaddress.ip_address(ip6)
        except ValueError:
            pass
        if not isinstance(addr, ipaddress.IPv6Address):
            logger.warning("Invalid IPv6 Address: %s", ip6)
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
