# webserver subprocess

import collections
import hashlib
import os
import signal
import sys
from pprint import pprint

import gunicorn.app.base
from flask import Flask, abort, current_app, jsonify, request

from moralis_streams_client import verify_signature

from .defaults import SERVER_ADDR, SERVER_PORT
from .tunnel import Tunnel

app = Flask(__name__)
app.config.update(event_queue=collections.deque([]))
app.config.update(shutdown_queue=collections.deque([]))
app.config.update(tunnel_url=None)
app.config.update(api_key=os.environ["MORALIS_API_KEY"].encode())


@app.route("/hello")
def hello():
    print(f"/hello: {request}")
    return dict(result={"message": "Hello, World!"}), 200


@app.route("/tunnel")
def tunnel():
    print(f"/tunnel: {request}")
    tunnel_url = current_app.config["tunnel_url"]
    return dict(result={"tunnel_url": tunnel_url}), 200


@app.route("/contract/event", methods=["POST"])
def contract_event():
    print(f"/contract/event: {request}")

    signature = request.headers["X-Signature"]
    api_key = current_app.config["api_key"]
    data = request.get_data()
    print(f"{data=}")
    verified = verify_signature(signature, request.get_data(), api_key)
    if verified is True:
        event = {}
        event["path"] = request.path
        event["method"] = request.method
        event["headers"] = {h[0]: h[1] for h in list(request.headers)}
        event["body"] = request.get_json()

        eq = current_app.config["event_queue"]
        eq.append(event)

        return {"result": "ok"}, 200
    else:
        return {"authorization": False}, 401


@app.route("/events")
def events():
    print(f"/events: {request}")
    eq = current_app.config["event_queue"]
    return dict(result=list(eq))


@app.route("/clear")
def clear():
    print(f"/clear: {request}")
    eq = current_app.config["event_queue"]
    eq.clear()
    return dict(result="cleared")


@app.after_request
def response_processor(response):
    q = current_app.config["shutdown_queue"]

    @response.call_on_close
    def _killer():
        if len(q):
            print(f"shutdown requested: {q.pop()}")
            os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)

    return response


@app.route("/shutdown")
def shutdown():
    print(f"/shutdown: {request}")
    q = current_app.config["shutdown_queue"]
    q.append(f"{request=}")
    return dict(result="shutdown pending"), 200


class GunicornServer(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def run(
    addr=SERVER_ADDR,
    port=SERVER_PORT,
    workers=1,
    level="info",
    tunnel=False,
    token=None,
    api=None,
):
    options = {"bind": f"{addr}:{port}", "workers": workers, "loglevel": level}
    server = GunicornServer(app, options)

    if api:
        app.config.update(streams_api=api)

    if tunnel:
        with Tunnel(port, token) as tunnel:
            app.config.update(tunnel_url=tunnel.public_url)
            ret = server.run()
    else:
        ret = server.run()
    return ret
