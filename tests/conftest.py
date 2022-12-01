# common test fixtures

import asyncio
import json
import logging
import multiprocessing as mp
import os
import queue
from pathlib import Path
from subprocess import run
from time import sleep, time

import MoralisSDK.api
import psutil
import pytest
from ape_apeman.context import APE
from eth_hash.auto import keccak
from eth_utils import to_checksum_address, to_hex

from moralis_streams_client import MoralisStreamsApi, defaults, server
from moralis_streams_client.signature import Signature
from moralis_streams_client.tunnel import NgrokTunnel
from moralis_streams_client.webhook import Webhook

info = logging.info

ECOSYSTEM = "ethereum"
NETWORK = "goerli"
PROVIDER = "alchemy"
CHAIN_ID = "0x5"


@pytest.fixture(scope="session", autouse=True)
def assert_startup_procs():
    assert (
        run(["pgrep", "ngrok"]).returncode != 0
    ), "ngrok processs running before test"
    assert (
        run(["pgrep", "webhook-server"]).returncode != 0
    ), "webhook process running before test"
    try:
        yield True
    finally:
        pass
        # run(["pkill", "ngrok"], check=False)
        # run(["pkill", "msc"], check=False)


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def event_keys():
    return ["body", "headers", "id", "method", "path", "relay"]


@pytest.fixture
def config():
    def _config(key):
        return os.environ[key]

    return _config


@pytest.fixture
def moralis(config):
    api = MoralisSDK.api.MoralisApi()
    api.set_api_key(config("MORALIS_API_KEY"))
    return api


@pytest.fixture(scope="module")
def webhook():
    return Webhook()


@pytest.fixture
def ecosystem():
    return ECOSYSTEM


@pytest.fixture
def network():
    return NETWORK


@pytest.fixture
def provider():
    return PROVIDER


@pytest.fixture
def chain_id():
    return CHAIN_ID


@pytest.fixture
def streams(api_key, api_url):
    return MoralisStreamsApi(api_key=api_key, url=api_url)


@pytest.fixture
def ape(ecosystem, network, provider):
    with APE(ecosystem=ecosystem, network=network, provider=provider) as ape:
        yield ape


@pytest.fixture
def system_address(config):
    address = config("TEST_SYSTEM_ADDRESS")
    return to_checksum_address(address)


@pytest.fixture
def system_key(config):
    return config("TEST_SYSTEM_KEY")


@pytest.fixture
def user_address(config):
    address = config("TEST_USER_ADDRESS")
    return to_checksum_address(address)


@pytest.fixture
def user_key(config):
    return config("TEST_USER_KEY")


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


@pytest.fixture
def ethersieve_contract_address(config):
    return config("ETHERSIEVE_CONTRACT_ADDRESS")


@pytest.fixture
def background_contract_address():
    return config("BACKGROUND_CONTRACT_ADDRESS")


def is_ok(response):
    return not response.is_error


def wait_for_it(address, port, timeout=15):
    time_expired = time() + timeout
    while (
        run(["nc", "-z", str(address), str(port)], check=False).returncode != 0
    ):
        assert time() < time_expired
        sleep(1)


class WebhookServerProcess:
    def __init__(
        self,
        addr=defaults.SERVER_ADDR,
        port=defaults.SERVER_PORT,
        tunnel=True,
        enable_buffer=True,
        debug=True,
        log_file="webhook.log",
    ):
        print("starting webhook_server...")
        self.addr = addr
        self.port = port
        self.log_file = log_file
        self.webhook = Webhook(
            addr=addr,
            port=port,
            tunnel=tunnel,
            debug=debug,
            enable_buffer=enable_buffer,
        )

    async def __aenter__(self):
        await self.webhook.start(
            wait=True, log_file=str(Path(".") / self.log_file)
        )
        wait_for_it(self.addr, self.port)
        assert await self.webhook.clear()
        info(await self.webhook.tunnel_url())
        procs = await self.webhook.processes()
        for proc in procs:
            info(proc)
        return self.webhook

    async def __aexit__(self, _type, exc, tb):
        def webhook_exit(proc):
            print(f"webhook_server {proc} terminated")

        print("\nstopping webhook_server processes...")
        await self.webhook.stop(wait=True, callback=webhook_exit)


@pytest.fixture
async def webhook_process():
    async with WebhookServerProcess() as webhook:
        yield webhook


@pytest.fixture
def webhook_process_class():
    return WebhookServerProcess


@pytest.fixture
def dump():
    def _dump(obj):
        info(json.dumps(obj, indent=2))

    return _dump


@pytest.fixture
async def webhook_tunnel_url(webhook):
    url = await webhook.tunnel_url()
    assert isinstance(url, str)
    assert url.startswith("http://")
    return url
