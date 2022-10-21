# webserver subprocess

import collections
import hashlib
import os
import signal
import sys
import uuid
from pprint import pprint

import gunicorn.app.base
import requests
from flask import Flask, abort, current_app, jsonify, request

from .api import MoralisStreamsApi
from .auth import Signature
from .defaults import SERVER_ADDR, SERVER_PORT
from .tunnel import NgrokTunnel

app = Flask(__name__)
app.config.update(event_queue=collections.deque([]))
app.config.update(shutdown_queue=collections.deque([]))
app.config.update(tunnel_url=None)
app.config.update(auth=Signature())
app.config.update(
    relay_header=os.environ.get("WEBHOOK_RELAY_HEADER", "X-API-Key")
)
app.config.update(relay_key=os.environ.get("WEBHOOK_RELAY_KEY", None))
app.config.update(relay_url=os.environ.get("WEBHOOK_RELAY_URL", None))
app.config.update(enable_buffer=os.environ.get("WEBHOOK_ENABLE_BUFFER", None))


@app.route("/inject", methods=["POST"])
def inject():
    print(f"{request.method} /inject: {request}")
    event = {}
    event["id"] = str(uuid.uuid4())
    event["path"] = request.path
    event["method"] = request.method
    event["headers"] = {h[0]: h[1] for h in list(request.headers)}
    event["body"] = request.get_json()
    event["relay"] = _relay(current_app.config, event)
    if current_app.config["enable_buffer"]:
        eq = current_app.config["event_queue"]
        eq.append(event)
    return dict(result={"injected": event["id"]}), 200

@app.route("/hello")
def hello():
    print(f"{request.method} /hello: {request}")
    return dict(result=dict(message="Hello, World!")), 200

@app.route("/tunnel")
def tunnel():
    print(f"{request.method} /tunnel: {request}")
    tunnel_url = current_app.config["tunnel_url"]
    return dict(result={"tunnel_url": tunnel_url}), 200


@app.route("/relay", methods=["POST", "GET"])
def relay():
    print(f"{request.method} /relay: {request}")
    if request.method == "POST":
        data = request.get_json()
        print(f"{data=}")
        relay_url = data["url"]
        current_app.config.update(relay_url=relay_url)
    elif request.method == "GET":
        relay_url = current_app.config["relay_url"]
    else:
        return dict(result={"method_not_allowed"}), 405

    return dict(result={"relay_url": relay_url}), 200


@app.route("/contract/event", methods=["POST"])
def contract_event():
    print(f"{request.method} /contract/event: {request}")

    data = request.get_data()
    print(f"{data=}")

    auth = current_app.config["auth"]
    signature = request.headers["X-Signature"]
    verified = auth.validate(signature, request.get_data())

    if verified is True:
        event = {}
        event["id"] = str(uuid.uuid4())
        event["path"] = request.path
        event["method"] = request.method
        event["headers"] = {h[0]: h[1] for h in list(request.headers)}
        event["body"] = request.get_json()
        event["relay"] = _relay(current_app.config, event)

        if current_app.config["enable_buffer"]:
            eq = current_app.config["event_queue"]
            eq.append(event)

        return dict(result="ok"), 200
    else:
        return dict(result="error", message="authorization failed"), 401


def _relay(config, event):
    ret = None
    relay_url = config["relay_url"]
    if relay_url:
        relay_header = config["relay_header"]
        relay_key = config["relay_key"]
        headers = event["headers"].copy()
        if relay_key:
            headers[relay_header] = relay_key
        result = requests.post(relay_url, headers=headers, json=event["body"])
        print(f"relay: {result}")
        ret = str(result)
    return ret


@app.route("/events")
def events():
    print(f"{request.method} /events")
    eq = current_app.config["event_queue"]

    # create a list from the event_queue, preserving order
    event_list = []
    tq = eq.copy()
    try:
        while True:
            event_list.append(tq.popleft())
    except IndexError:
        pass

    return dict(result=event_list)


@app.route("/clear")
def clear():
    print(f"{request.method} /clear")
    eq = current_app.config["event_queue"]
    eq.clear()
    return dict(result="cleared")


@app.route("/event/<event_id>", methods=["DELETE", "GET"])
def event(event_id):
    print(f"{request.method} /event/{event_id}")
    eq = current_app.config["event_queue"]
    tq = eq.copy()
    eq.clear()
    found = None
    try:
        while True:
            event = tq.popleft()
            if event["id"] == event_id:
                found = event
                if request.method == "DELETE":
                    event = None
            if event:
                eq.append(event)
    except IndexError:
        pass

    if found is None:
        return dict(result="error", message=f"event {event_id} not found"), 404
    else:
        return dict(result=event), 200


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


class ServerProcess:
    def __init__(self, config):
        addr = config.get("addr", SERVER_ADDR)
        self.port = int(config.get("port", SERVER_PORT))
        self.tunnel = config.get("tunnel", True)
        self.token = config.get("ngrok_token", os.environ["NGROK_AUTHTOKEN"])
        workers = int(config.get("workers", "1"))
        debug = config.get("debug", False)
        options = {
            "bind": f"{addr}:{self.port}",
            "workers": workers,
            "loglevel": "debug" if debug else "info",
        }
        self.server = GunicornServer(app, options)

    def run(self):
        if self.tunnel is True:
            with NgrokTunnel(self.port, self.token) as tunnel:
                app.config.update(tunnel_url=tunnel.public_url)
                return self.server.run()
        else:
            return self.server.run()
