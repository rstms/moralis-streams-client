# common test fixtures

import json
import logging
import multiprocessing as mp
import os
import queue
from subprocess import check_call
from time import sleep

import attr
import pytest
import requests
from eth_hash.auto import keccak
from eth_utils import to_hex

from moralis_streams_client import (
    MoralisStreamsApi,
    Signature,
    defaults,
    server,
)
from moralis_streams_client.tunnel import NgrokTunnel


@pytest.fixture
def config():
    def _config(key):
        return os.environ[key]

    return _config


@pytest.fixture
def api_key(config):
    return config("MORALIS_API_KEY")


@pytest.fixture
def api_url():
    return defaults.STREAMS_URL


@pytest.fixture
def server_addr():
    return defaults.SERVER_ADDR


@pytest.fixture
def server_port():
    return defaults.SERVER_PORT


@attr.s(auto_attribs=True)
class Callback:

    q = mp.Queue(defaults.QSIZE)

    def put(self, item):
        self.q.put(item, False)
        while self.empty() is True or self.size() < 1:
            sleep(0.001)

    def get(self, block=True, timeout=None):
        return self.q.get(block, timeout)

    def list(self, block=True, timeout=None, sentinel=None, count=None):
        items = []
        # print(f"list_enter {self} q_size={self.q.qsize()} q_empty={self.q.empty()} items={len(items)}")
        while True:
            try:
                item = self.q.get(block, timeout)
            except queue.Empty:
                break
            items.append(item)
            if sentinel is not None and item == sentinel:
                break
            if count is not None and len(items) >= count:
                break
        return items

    def clear(self):
        try:
            while not self.empty():
                self.get(False)
        except queue.Empty:
            pass

    def empty(self):
        return self.q.empty()

    def size(self):
        return self.q.qsize()


@pytest.fixture()
def callbacks():
    try:
        cb = Callback()
        # print(f"callbacks: yielding {cb} {cb.queue}")
        yield cb
    finally:
        pass
        # print(f"callbacks: releasing {cb} {cb.queue}")


def server_run(*args, **kwargs):
    from moralis_streams_client.server import ServerProcess

    return ServerProcess(kwargs).run()


@pytest.fixture(scope="session", autouse=True)
def webhook_server():
    try:
        print("starting webhook_server...")
        p = mp.Process(
            target=server_run,
            kwargs={
                "addr": defaults.SERVER_ADDR,
                "port": defaults.SERVER_PORT,
                "tunnel": True,
            },
        )
        p.start()
        ret = check_call(
            [
                "wait-for-it",
                "-s",
                f"{defaults.SERVER_ADDR}:{defaults.SERVER_PORT}",
            ]
        )
        assert ret == 0, "timeout waiting for webhook_server listen port"

        yield p
    finally:
        # response = requests.get(f"http://{defaults.SERVER_ADDR}:{defaults.SERVER_PORT}/shutdown")
        # print(f"{response}")
        p.terminate()
        p.join()
        check_call(["pkill", "ngrok"])
    print("webhook_server exited")


@pytest.fixture
def dump():
    def _dump(obj):
        logging.info(json.dumps(obj, indent=2))

    return _dump


@pytest.fixture
def calculate_signature(api_key):
    signature = Signature(api_key)

    def _calculate_signature(body):
        return signature.calculate(body)

    return _calculate_signature


@pytest.fixture
def webhook(server_addr, server_port, calculate_signature, dump):
    def _webhook(path, params=None, json_data=None):
        url = f"http://{server_addr}:{server_port}/{path}"
        if json_data:
            headers = {}
            if path == "contract/event":
                data = json.dumps(json_data)
                dump(f"{data=}")
                headers["X-Signature"] = calculate_signature(data.encode())
            response = requests.post(url, json=json_data, headers=headers)
        else:
            response = requests.get(url, params=params)
        assert response.ok
        result = response.json()
        assert isinstance(result, dict)
        assert "result" in result
        return result

    return _webhook


@pytest.fixture
def webhook_tunnel_url(webhook):
    ret = webhook("tunnel")
    assert isinstance(ret, dict)
    tunnel = ret["result"]
    assert isinstance(tunnel, dict)
    assert len(tunnel.keys()) == 1
    url = list(tunnel.values())[0]
    return url


@pytest.fixture
def streams_api(api_key, api_url):
    return MoralisStreamsApi(api_key=api_key, url=api_url)
