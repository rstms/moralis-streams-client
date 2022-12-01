# webhook server process

import json
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import httpx
import psutil

from . import settings
from .logconfig import configure_logging
from .signature import Signature

logger = logging.getLogger(__name__)
debug = logger.debug

PROCESS_START_TIMEOUT = 5
PROCESS_STOP_TIMEOUT = 10


class Webhook:
    def __init__(
        self,
        *,
        debug=None,
        addr=None,
        port=None,
        base_url=None,
        tunnel=None,
        relay_url=None,
        relay_key=None,
        relay_header=None,
        enable_buffer=None,
        moralis_api_key=None,
        log_level=None,
        log_file=None,
    ):
        self.debug = settings.DEBUG if debug is None else debug
        self.addr = addr or settings.ADDR
        self.port = port or settings.PORT
        self.tunnel = settings.TUNNEL if tunnel is None else tunnel
        self.relay_url = relay_url or settings.RELAY_URL
        self.relay_key = relay_key or settings.RELAY_KEY
        self.relay_header = relay_header or settings.RELAY_HEADER
        self.enable_buffer = (
            settings.BUFFER_ENABLE if enable_buffer is None else enable_buffer
        )
        self.moralis_api_key = moralis_api_key or settings.MORALIS_API_KEY
        self.log_level = log_level or settings.LOG_LEVEL
        self.log_file = log_file or settings.LOG_FILE
        base_url = base_url or f"http://{self.addr}:{self.port}/"
        self.base_url = base_url.strip("/") + "/"
        self.signature = Signature()
        self.proc = None
        configure_logging()

    async def _request(self, method, path, **kwargs):
        # generate a signature checksum
        raise_for_status = kwargs.pop("raise_for_status", True)
        kwargs.setdefault("json", None)
        kwargs.setdefault("headers", {})
        if kwargs["json"] is None:
            body = b""
        else:
            body = kwargs["json"]
        kwargs["headers"].update(self.signature.headers(body))

        async with httpx.AsyncClient() as client:
            self.response = await client.request(
                method, self.base_url + path, **kwargs
            )
        if raise_for_status:
            self.response.raise_for_status()
        body = self.response.json()
        return body["result"]

    async def hello(self):
        """send and receive a friendly greeting"""
        return await self._request("GET", "hello")

    async def clear(self):
        """clear the event buffer"""
        return await self._request("GET", "clear")

    async def tunnel_url(self):
        """return the tunnel url"""
        return await self._request("GET", "tunnel")

    async def buffer(self, enable=None):
        """set buffer enable"""
        if enable is None:
            method = "GET"
            args = {}
        else:
            method = "POST"
            args = dict(enable=enable)

        return await self._request(method, "buffer", json=args)

    async def relay(self, url=None, key=None, header=None, enable=None):
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

        return await self._request(method, "relay", json=args)

    async def inject(self, event):
        """process an event as a received callback"""
        return await self._request("POST", "contract/event", json=event)

    async def event(self, event_id):
        """return event by id"""
        return await self._request("GET", f"event/{event_id}")

    async def delete(self, event_id):
        """delete event by id"""
        return await self._request("DELETE", f"event/{event_id}")

    async def events(self):
        """return a list of all events"""
        return await self._request("GET", "events")

    async def shutdown(self):
        """request server shutdown"""
        return await self._request("GET", "shutdown")

    async def start(self, wait=True, log_file=None):
        """start a server process"""
        env = os.environ.copy()

        if log_file:
            self.log_file = log_file

        env["WEBHOOK_ADDR"] = self.addr
        env["WEBHOOK_PORT"] = str(self.port)
        env["WEBHOOK_LOG_FILE"] = str(self.log_file)
        env["WEBHOOK_LOG_LEVEL"] = str(self.log_level)
        env["WEBHOOK_DEBUG"] = "1" if self.debug else "0"
        env["WEBHOOK_TUNNEL"] = "1" if self.tunnel else "0"
        env["WEBHOOK_BUFFER_ENABLE"] = "1" if self.enable_buffer else "0"
        if self.relay_url:
            env["WEBHOOOK_RELAY_URL"] = self.relay_url
        if self.relay_header:
            env["WEBHOOOK_RELAY_HEADER"] = self.relay_header
        if self.relay_key:
            env["WEBHOOK_RELAY_KEY"] = str(self.relay_key)
        if self.moralis_api_key:
            env["WEBHOOK_API_KEY"] = str(self.moralis_api_key)

        cmd = ["webhook-server", "--port", str(self.port)]
        debug(f"{cmd=}")
        for k, v in env.items():
            if k.startswith("WEBHOOK"):
                debug(f"  {k}={v}")

        pid = subprocess.Popen(
            cmd,
            env=env,
            stderr=subprocess.STDOUT,
            stdout=subprocess.DEVNULL,
            close_fds=True,
        ).pid
        debug(f"{pid=}")

        if wait:
            timeout = time.time() + PROCESS_START_TIMEOUT
            while await self.server_running() is False:
                time.sleep(0.25)
                if time.time() > timeout:
                    raise TimeoutError
        return pid

    async def processes(self):
        """return list of server processess"""
        pattern = f".*webhook.*--port {self.port}.*"
        procs = []
        for p in psutil.process_iter():
            cmdline = " ".join(p.cmdline())
            if re.match(pattern, cmdline):
                debug(f"process: {p}")
                procs.append(p)
        return procs

    async def server_running(self):
        """return bool indicating if server is running"""
        return bool(await self.processes())

    async def stop(self, wait=True, callback=None):
        """signal running server processes to terminate"""
        if await self.server_running():
            procs = await self.processes()
            for p in procs:
                debug(f"terminate: {p}")
                p.terminate()

            if wait:
                gone, alive = psutil.wait_procs(
                    await self.processes(),
                    timeout=PROCESS_STOP_TIMEOUT,
                    callback=callback,
                )
                for p in alive:
                    p.kill()

                if await self.server_running():
                    await self.shutdown()

            timeout = time.time() + PROCESS_STOP_TIMEOUT
            while wait and await self.server_running():
                time.sleep(0.25)
                if time.time() > timeout:
                    raise TimeoutError
