# common test fixtures

import json
import logging
import multiprocessing as mp
import os
import queue
from pathlib import Path
from subprocess import check_call
from time import sleep

import attr
import MoralisSDK.api
import pytest
import requests
from ape_apeman import APE
from eth_hash.auto import keccak
from eth_utils import to_checksum_address, to_hex

from moralis_streams_client import (
    MoralisStreamsApi,
    Signature,
    Webhook,
    defaults,
    server,
)
from moralis_streams_client.tunnel import NgrokTunnel

info = logging.info

ECOSYSTEM = "ethereum"
NETWORK = "goerli"
PROVIDER = "alchemy"
CHAIN_ID = "0x5"


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


@pytest.fixture(scope="session")
def wait_for_it():
    def _wait_for_it(address, port):
        check_call(
            [
                "wait-for-it",
                "-s",
                f"{address}:{port}",
            ]
        )

    return _wait_for_it


@pytest.fixture(scope="session", autouse=True)
def webhook_server():
    print("starting webhook_server...")
    kwargs = {
        "addr": defaults.SERVER_ADDR,
        "port": defaults.SERVER_PORT,
        "tunnel": True,
        "debug": True,
        "enable_buffer": True,
    }
    webhook = Webhook(**kwargs)
    webhook.start(wait=True, logfile=str(Path(".") / "webhook.log"))
    check_call(
        [
            "wait-for-it",
            "-s",
            f"{defaults.SERVER_ADDR}:{defaults.SERVER_PORT}",
        ]
    )
    assert webhook.clear()
    info(webhook.tunnel_url())
    procs = webhook.processes()
    for proc in procs:
        info(proc)
    try:
        yield webhook
    finally:
        pass
        # webhook.shutdown()
    print("webhook_server exited")


@pytest.fixture
def dump():
    def _dump(obj):
        info(json.dumps(obj, indent=2))

    return _dump


@pytest.fixture
def calculate_signature(api_key):
    signature = Signature(api_key)

    def _calculate_signature(body):
        return signature.calculate(body)

    return _calculate_signature


@pytest.fixture
def webhook_tunnel_url(webhook):
    url = webhook.tunnel_url()
    assert isinstance(url, str)
    assert url.startswith("http://")
    return url
