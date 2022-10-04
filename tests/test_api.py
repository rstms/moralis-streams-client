# api tests

import os

import pytest

from moralis_streams_client.api import connect

GOERLI_HEX_ID = "0x5"


@pytest.fixture
def api():
    key = os.environ["MORALIS_API_KEY"]
    return connect(key=key, format_dict=True)


def test_api_get_stats(api, dump):
    ret = api.get_stats()
    assert isinstance(ret, dict)
    dump(ret)


"""
def test_api_create_stream(api, dump, test_contract_address):
    ret = api.create_stream(
        webhook_url=str,
        description = "moralis_streams_client testing stream",
        tag: "client_test",
        chain_ids: [GOERLI_HEX_ID],
        stream_type: "contract",
        address: test_contract_address,
        topic: str = None,
        include_native_txs: bool = False,
        abi: dict = None,
        filter_: StreamsFilter = None)
    assert isinstance(ret, dict)
    dump(ret)
"""
