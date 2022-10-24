# webserver subprocess

import collections
import hashlib
import logging
import os
import signal
import sys
import uuid
from pprint import pprint

import gunicorn.app.base
import requests
from flask import Flask, Response, abort, current_app, g, jsonify, request
from requests.structures import CaseInsensitiveDict

from .api import MoralisStreamsApi
from .defaults import (
    RELAY_ID_HEADER,
    RELAY_KEY_HEADER,
    SERVER_ADDR,
    SERVER_PORT,
)
from .signature import Signature
from .tunnel import NgrokTunnel

app = Flask(__name__)


class EventQueue:
    def __init__(self, config):
        self.events = collections.deque([])
        self.buffer_enabled = config.get(
            "buffer_enabled",
            bool(os.environ.get("WEBHOOK_BUFFER_ENABLE", True)),
        )
        self.relay_url = config.get(
            "relay_url", os.environ.get("WEBHOOK_RELAY_URL", None)
        )
        self.relay_key = config.get(
            "relay_key", os.environ.get("WEBHOOK_RELAY_KEY", None)
        )
        self.relay_header = config.get(
            "relay_header",
            os.environ.get("WEBHOOK_RELAY_HEADER", RELAY_KEY_HEADER),
        )

    def append(self, event):
        if self.relay_url:
            _response = self.forward(event)
            event["relay"] = dict(
                url=_response.url,
                status_code=_response.status_code,
                text=_response.text,
                headers=dict(_response.headers),
            )
            response = (
                _response.text,
                _response.status_code,
                [(k, v) for k, v in _response.headers.items()],
            )
        else:
            event["relay"] = None
            response = dict(result=event["id"])
        if self.buffer_enabled:
            self.events.append(event)
        return response

    def forward(self, event):
        headers = CaseInsensitiveDict(event["headers"])
        if self.relay_header and self.relay_key:
            headers[self.relay_header] = self.relay_key
        headers[RELAY_ID_HEADER] = event["id"]
        return requests.post(
            self.relay_url, headers=headers, json=event["body"]
        )

    def list(self):
        # create a list from the event_queue, preserving order
        ret = []
        tq = self.events.copy()
        try:
            while True:
                ret.append(tq.popleft())
        except IndexError:
            pass
        return ret

    def clear(self):
        self.events.clear()
        return "cleared"

    def lookup(self, event_id, delete):
        tq = self.events.copy()
        if delete:
            self.events.clear()
        found = None
        while True:
            try:
                event = tq.popleft()
                if event["id"] == event_id:
                    found = event
                    if delete is False:
                        break
                elif delete is True:
                    self.events.append(event)
            except IndexError:
                break
        return found


app.config.update(event_queue=EventQueue(app.config))
app.config.update(tunnel_url=None)
app.config.update(signature=Signature(api_key=os.environ["WEBHOOK_API_KEY"]))


def header_key(key):
    return "-".join([k.capitalize() for k in key.split("-")])


@app.before_request
def validate_signature():
    current_app.logger.info(
        f"{request.method} {request.path} {list(request.args)} ({len(request.get_data())} bytes)"
    )
    signature = current_app.config["signature"]
    header = signature.header
    if header not in request.headers:
        return "missing signature", request.codes.BAD_REQUEST
    if not signature.validate(request.headers[header], request.get_data()):
        return "authorization failed", requests.codes.UNAUTHORIZED
    g.config = current_app.config
    g.events = g.config["event_queue"]
    g.killswitch = False


def _response(result, code=requests.codes.OK):
    return dict(result=result), code


@app.route("/hello")
def hello():
    return _response("Hello, World!")


@app.route("/tunnel")
def tunnel():
    return _response(g.config["tunnel_url"])


@app.route("/buffer", methods=["GET", "POST"])
def buffer():
    if request.method == "POST":
        g.events.buffer_enabled = request.json.get("enable")
    return _response(g.events.buffer_enabled)


@app.route("/relay", methods=["GET", "POST"])
def relay():
    if request.method == "POST":
        g.events.relay_url = request.json["url"]
        g.events.relay_header = request.json["header"]
        g.events.relay_key = request.json["key"]
    return _response(
        dict(
            url=g.events.relay_url,
            header=g.events.relay_header,
            key=g.events.relay_key,
        )
    )


@app.route("/contract/event", methods=["POST"])
def contract_event():
    event = dict(
        id=str(uuid.uuid4()),
        path=request.path,
        method=request.method,
        headers={header_key(k): v for k, v in request.headers},
        body=request.json,
    )
    return g.events.append(event)


@app.route("/events")
def events():
    return _response(g.events.list())


@app.route("/clear")
def clear():
    return _response(g.events.clear())


@app.route("/event/<event_id>", methods=["DELETE", "GET"])
def event(event_id):

    if request.method == "GET":
        event = g.events.lookup(event_id, delete=False)
    elif request.method == "DELETE":
        event = g.events.lookup(event_id, delete=True)
    else:
        return _response("error", requests.codes.METHOD_NOT_ALLOWED)

    if event_id is None:
        return _response(
            f"event {event_id} not found", requests.codes.NOT_FOUND
        )
    else:
        return _response(event)


@app.after_request
def response_processor(response):
    killswitch = g.killswitch

    @response.call_on_close
    def _killer():
        if killswitch:
            os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)

    return response


@app.route("/shutdown")
def shutdown():
    g.killswitch = True
    return _response("shutdown pending", requests.codes.OK)


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
        print("ServerProcess")
        for k, v in config.items():
            print(f"  {k}={v}")
        addr = config.get("addr", SERVER_ADDR)
        self.port = int(config.get("port", SERVER_PORT))
        self.tunnel = config.get("tunnel", True)
        self.token = config.get("ngrok_token", os.environ["NGROK_AUTHTOKEN"])
        workers = int(config.get("workers", "1"))
        debug = config.get("debug", False)
        config["MAX_CONTENT_LENGTH"] = os.environ.get(
            "WEBHOOK_MAX_CONTENT_LENGTH", 1_000_000_000
        )
        app.config.update(config)
        options = {
            "bind": f"{addr}:{self.port}",
            "workers": workers,
            "loglevel": "debug" if debug else "info",
            "debug": debug,
        }
        self.server = GunicornServer(app, options)

    def run(self):
        if self.tunnel is True:
            print(f"starting ngrok tunnel {self.tunnel=}")
            with NgrokTunnel(self.port, self.token) as tunnel:
                app.config.update(tunnel_url=tunnel.public_url)
                return self.server.run()
        else:
            print(f"ngrok tunnel disabled: {self.tunnel=}")
            app.config.update(tunnel_url=None)
            return self.server.run()
