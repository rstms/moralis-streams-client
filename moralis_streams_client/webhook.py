# webhook server process

import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from subprocess import DEVNULL, STDOUT, CalledProcessError, Popen, check_output

import psutil
import requests

from .signature import Signature

logger = logging.getLogger(__name__)
debug = logger.debug

PROCESS_START_TIMEOUT = 5
PROCESS_STOP_TIMEOUT = 10


class Webhook:
    def __init__(
        self,
        *,
        addr="127.0.0.1",
        port=8080,
        debug=False,
        base_url=None,
        tunnel=True,
        relay_url=None,
        relay_key=None,
        relay_header=None,
        enable_buffer=True,
        moralis_api_key=None,
    ):
        self.debug = debug
        self.addr = addr
        self.port = port
        base_url = base_url or f"http://{addr}:{port}/"
        self.base_url = base_url.strip("/") + "/"
        self.tunnel = tunnel
        self.relay_url = relay_url
        self.relay_key = relay_key
        self.relay_header = relay_header
        self.enable_buffer = enable_buffer
        self.moralis_api_key = moralis_api_key
        self.signature = Signature()
        self.proc = None

    def _request(self, method, path, **kwargs):
        # generate a signature checksum
        raise_for_status = kwargs.pop("raise_for_status", True)
        kwargs.setdefault("json", None)
        kwargs.setdefault("headers", {})
        if kwargs["json"] is None:
            body = b""
        else:
            body = json.dumps(kwargs["json"]).encode()
        kwargs["headers"].update(self.signature.headers(body))

        self.response = requests.request(
            method, self.base_url + path, **kwargs
        )
        if raise_for_status:
            self.response.raise_for_status()
        body = self.response.json()
        return body["result"]

    def hello(self):
        """send and receive a friendly greeting"""
        return self._request("GET", "hello")

    def clear(self):
        """clear the event buffer"""
        return self._request("GET", "clear")

    def tunnel_url(self):
        """return the tunnel url"""
        return self._request("GET", "tunnel")

    def buffer(self, enable=None):
        """set buffer enable"""
        if enable is None:
            method = "GET"
            args = {}
        else:
            method = "POST"
            args = dict(enable=enable)

        return self._request(method, "buffer", json=args)

    def relay(self, url=None, key=None, header=None, enable=None):
        """update relay configuraton"""
        args = {}
        method = "GET"
        if enable is None and url is not None:
            enable = True
        if enable is True:
            method = "POST"
            args["url"] = url
            args["key"] = key
            args["header"] = header
        elif enable is False:
            method = "POST"
            args["url"] = None
            args["key"] = None
            args["header"] = None

        return self._request(method, "relay", json=args)

    def inject(self, event):
        """process an event as a received callback"""
        return self._request("POST", "contract/event", json=event)

    def event(self, event_id):
        """return event by id"""
        return self._request("GET", f"event/{event_id}")

    def delete(self, event_id):
        """delete event by id"""
        return self._request("DELETE", f"event/{event_id}")

    def events(self):
        """return a list of all events"""
        return self._request("GET", "events")

    def shutdown(self):
        """request server shutdown"""
        return self._request("GET", "shutdown")

    def start(self, logfile=None, wait=True):
        """start a server process"""
        if logfile is None:
            logfile = DEVNULL
        else:
            logfile = Path(logfile).open("a") or DEVNULL
        cmd = ["msc"]
        cmd.extend(["webhook", "--addr", self.addr, "--port", str(self.port)])
        if self.debug:
            cmd.append("--debug")
        if self.tunnel:
            cmd.append("--tunnel")
        else:
            cmd.append("--no-tunnel")
        env = os.environ.copy()
        if self.enable_buffer:
            cmd.append("--enable-buffer")
        else:
            cmd.append("--disable-buffer")
        if self.relay_url:
            cmd.extend(["--relay-url", self.relay_url])
        if self.relay_header:
            cmd.extend(["--relay-header", self.relay_header])
        if self.relay_key:
            env["WEBHOOK_RELAY_KEY"] = self.relay_key
        if self.moralis_api_key:
            env["WEBHOOK_API_KEY"] = self.moralis_api_key

        env["PYTHONUNBUFFERED"] = "1"

        cmd.append("server")

        debug(f"command: {cmd}")
        for k, v in env.items():
            if k.startswith("WEBHOOK"):
                debug(f"  {k}={v}")

        self.proc = Popen(
            cmd,
            env=env,
            stderr=STDOUT,
            stdout=logfile,
            bufsize=1,
        )

        if wait:
            timeout = time.time() + PROCESS_START_TIMEOUT
            while self.server_running() is False:
                time.sleep(0.25)
                if time.time() > timeout:
                    raise TimeoutError

        return self.proc

    def processes(self):
        """return list of server processess"""
        pattern = f".*webhook.*--port {self.port}.*"
        procs = []
        for p in psutil.process_iter():
            cmdline = " ".join(p.cmdline())
            if re.match(pattern, cmdline):
                procs.append(p)
        return procs

    def server_running(self):
        """return bool indicating if server is running"""
        return bool(self.processes())

    def stop(self, wait=True, callback=None):
        """signal running server processes to terminate"""
        if self.server_running():
            procs = self.processes()
            for p in procs:
                p.terminate()

            if wait:
                gone, alive = psutil.wait_procs(
                    self.processes(),
                    timeout=PROCESS_STOP_TIMEOUT,
                    callback=callback,
                )
                for p in alive:
                    p.kill()

                if self.server_running():
                    self.shutdown()

            timeout = time.time() + PROCESS_STOP_TIMEOUT
            while wait and self.server_running():
                time.sleep(0.25)
                if time.time() > timeout:
                    raise TimeoutError
