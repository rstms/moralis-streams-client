# api tests

import logging
import os
import time
from decimal import Decimal
from pathlib import Path

import MoralisSDK.api
import pytest
from backoff import expo, on_exception
from box import Box, BoxList
from eth_account import Account
from eth_utils import (
    event_abi_to_log_topic,
    from_wei,
    is_same_address,
    to_checksum_address,
    to_hex,
    to_wei,
)
from ratelimit import RateLimitException, limits

import moralis_streams_client
from moralis_streams_client import models

# TODO: generate history and multiple streams to ensure enough response data

debug = logging.debug
info = logging.info
logging.getLogger("moralis_streams_client.api").setLevel("WARNING")


ETHERSCAN_LIMIT_COUNT = 5
ETHERSCAN_LIMIT_SECONDS = 1

CONFIRM_COUNT = 12

EVENT_NAME = "PrintMintPending"

CALLBACK_TIMEOUT = 300

CALLBACK_TEST_KEYS = [
    "abi",
    "block",
    "chainId",
    "confirmed",
    "erc20Approvals",
    "erc20Transfers",
    "logs",
    "nftApprovals",
    "nftTransfers",
    "retries",
    "txs",
    "txsInternal",
    "streamId",
    "tag",
]


@pytest.fixture
def event_name():
    return EVENT_NAME


@pytest.fixture
def background_contract_address(config):
    address = config("TEST_BACKGROUND_CONTRACT")
    return to_checksum_address(address)


# rate-limit etherscan api calls
@on_exception(expo, RateLimitException, max_tries=16)
@limits(calls=ETHERSCAN_LIMIT_COUNT, period=ETHERSCAN_LIMIT_SECONDS)
def limit(func, *args, **kwargs):
    return func(*args, **kwargs)


@pytest.fixture
def get_contract_tokens(moralis, network):
    def _get_contract_tokens(contract_address):
        owners = Box(moralis.get_nft_owners(contract_address, chain=network))
        assert "result" in owners
        return owners.result

    return _get_contract_tokens


def test_api_transactions(ape, get_contract_tokens, system_address, moralis):
    assert ape.explorer
    txns = list(limit(ape.explorer.get_account_transactions, system_address))
    assert txns
    contracts = set()
    for txn in txns:
        info(f"{txn.transaction}")
        to_addr = txn.transaction.dict()["to"]
        if to_addr == "":
            assert txn.contract_address
            contracts.add(to_checksum_address(txn.contract_address))

    info(f"txn_count={len(txns)}")
    info(f"contracts={len(contracts)}")
    for addr in contracts:
        contract = ape.Contract(addr)
        info(f"{contract.symbol()} {contract}")

        url = ape.explorer.get_address_url(addr)
        info(url)

        token_ids = Box(moralis.get_token_id(addr, chain="goerli"))
        info(f"  tokens={int(token_ids.total)}")

        tokens = get_contract_tokens(addr)
        assert token_ids.total == len(tokens)
        for token in tokens:
            info(f"  {int(token.token_id)}: {token.name} {token.owner_of}")


@pytest.fixture
def ethersieve_contract(ape, ethersieve_contract_address):
    return ape.Contract(ethersieve_contract_address)


@pytest.fixture
def background_contract(ape, background_contract_address):
    return ape.Contract(background_contract_address)


@pytest.mark.uses_gas
def test_api_create_stream(
    streams,
    dump,
    chain_id,
    ethersieve_contract,
    background_contract,
    event_name,
    event_keys,
    get_contract_tokens,
    system_address,
    system_key,
    user_address,
    user_key,
    ape,
    webhook,
    webhook_tunnel_url,
):
    webhook.clear()

    streams_begin = streams.get_streams()

    event_abi = ethersieve_contract.contract_type.events[event_name].dict()
    event_topic = to_hex(event_abi_to_log_topic(event_abi))
    contract_abi = ethersieve_contract.contract_type.dict()["abi"]

    stream = Box(
        streams.create_stream(
            webhook_url=webhook_tunnel_url + "/contract/event",
            description="moralis_streams_client testing stream",
            tag="msc_test",
            topic0=[event_topic],
            all_addresses=False,
            include_native_txs=True,
            include_contract_logs=True,
            include_internal_txs=True,
            abi=contract_abi,
            advanced_options=None,
            chain_ids=[chain_id],
        )
    )
    dump(f"{stream.id=}")
    dump(f"{stream.tag=}")
    dump(f"{stream.status=}")
    dump(f"{stream.statusMessage=}")
    address_added = Box(
        streams.add_address_to_stream(stream.id, [ethersieve_contract.address])
    )
    assert isinstance(address_added, dict)
    dump(address_added)
    assert "streamId" in address_added
    assert "address" in address_added
    assert isinstance(address_added.streamId, str)
    assert isinstance(address_added.address, list)
    addresses = address_added.address
    for address in addresses:
        assert isinstance(address, str)
        assert is_same_address(address, ethersieve_contract.address)

    background_ids = []
    for token in get_contract_tokens(background_contract.address):
        if is_same_address(token.owner_of, user_address):
            background_ids.append(token.token_id)
    dump(f"user background tokens: {background_ids}")

    ethersieve_ids = []
    for token in get_contract_tokens(ethersieve_contract.address):
        if is_same_address(token.owner_of, user_address):
            ethersieve_ids.append(token.token_id)
    dump(f"user ethersieve tokens: {ethersieve_ids}")

    # send a printMint transaction from user to ethersieve

    PRIORITY_FEE_GWEI = 3

    user = Account().from_key(user_key)
    max_priority_fee = ape.provider.priority_fee + to_wei(
        PRIORITY_FEE_GWEI, "gwei"
    )

    info(f"max_priority_fee={from_wei(max_priority_fee, 'gwei')} gwei")

    args = (0, 0, 1, 2, 3)
    kwargs = dict(
        value=to_wei(Decimal(".01"), "ether"),
        sender=user.address,
        nonce=ape.provider.get_nonce(user.address),
        max_priority_fee=max_priority_fee,
        required_confirmations=0,
    )
    txn = ethersieve_contract.printMint.as_transaction(*args, **kwargs)
    txn.signature = user.sign_transaction(txn.dict())
    estimated_gas = ape.provider.estimate_gas_cost(txn)
    info(f"{estimated_gas=}")
    receipt = ape.provider.send_transaction(txn)

    dump(dict(txn_hash=receipt.txn_hash, status=str(receipt.status)))

    CONFIRM_COUNT = 2

    confirmed_height = receipt.block_number + CONFIRM_COUNT
    last_height = receipt.block_number

    info(f"Waiting for {CONFIRM_COUNT} confirmations...")
    count = 1
    while last_height < confirmed_height:
        height = ape.provider.chain_manager.blocks.height
        if last_height != height:
            info(f"block[{count} of {CONFIRM_COUNT}]: {height}")
            last_height = height
            count += 1

    info(f"Waiting up to {CALLBACK_TIMEOUT} seconds for 3 callback events...")
    events = {}

    timeout = time.time() + CALLBACK_TIMEOUT
    while len(events) < 3:
        assert time.time() < timeout, "timeout waiting for 3 callback events"
        all_events = webhook.events()
        for event in all_events:
            event_id = event["id"]
            if event_id not in events:
                events[event_id] = event
                info(f"{event_id=}")
        time.sleep(1)

    events = webhook.events()
    assert isinstance(events, list)
    for event in events:
        assert isinstance(event, dict)
        assert set(event.keys()) == set(event_keys)

    assert set(events[0]["body"].keys()) == set(CALLBACK_TEST_KEYS)
    unconfirmed = events[1]["body"]
    assert unconfirmed["confirmed"] is False
    confirmed = events[2]["body"]
    assert confirmed["confirmed"] is True
    for e in [unconfirmed, confirmed]:
        assert len(e["txs"]) == 1
        assert is_same_address(e["txs"][0]["fromAddress"], user_address)
        assert is_same_address(
            e["txs"][0]["toAddress"], ethersieve_contract.address
        )

    result = Box(streams.delete_stream(stream.id))
    assert result.id == stream.id

    streams_end = streams.get_streams()

    assert len(streams_begin) == len(streams_end)


def test_api_get_streams_default(streams):
    all_streams = streams.get_streams()
    assert isinstance(all_streams, list)
    for i, stream in enumerate(all_streams):
        assert isinstance(stream, dict)
        info(f"{i}: {stream['id']}")


def test_api_get_streams_row_limit(streams, monkeypatch):
    # set low row limit to ensure paging
    monkeypatch.setattr(streams, "row_limit", 3)
    streams = streams.get_streams()
    assert isinstance(streams, list)
    for i, stream in enumerate(streams):
        assert isinstance(stream, dict)
        info(f"{i}: {stream['id']}")


def test_api_get_streams_row_page_limit(streams, monkeypatch):
    # set low row and page limit to ensure paging
    monkeypatch.setattr(streams, "row_limit", 2)
    monkeypatch.setattr(streams, "page_limit", 2)
    all_streams = streams.get_streams()
    assert isinstance(all_streams, list)
    for i, stream in enumerate(all_streams):
        assert isinstance(stream, dict)
        info(f"{i}: {stream['id']}")


def test_api_get_history_default(streams):
    history_events = streams.get_history()
    assert isinstance(history_events, list)
    for i, history_event in enumerate(history_events):
        assert isinstance(history_event, dict)
        info(f"{i}: {history_event['id']}")


def test_api_get_history_row_limit(streams, monkeypatch):
    # set low row limit to ensure paging
    monkeypatch.setattr(streams, "row_limit", 3)
    history_events = streams.get_history()
    assert isinstance(history_events, list)
    for i, history_event in enumerate(history_events):
        assert isinstance(history_event, dict)
        info(f"{i}: {history_event['id']}")


def test_api_get_history_row_page_limit(streams, monkeypatch):
    # set low row and page limit to ensure paging
    monkeypatch.setattr(streams, "row_limit", 3)
    monkeypatch.setattr(streams, "page_limit", 2)
    history_events = streams.get_history()
    assert isinstance(history_events, list)
    for i, history_event in enumerate(history_events):
        assert isinstance(history_event, dict)
        info(f"{i}: {history_event['id']}")


def test_api_delete_all_streams(streams, dump):
    all_streams = streams.get_streams()
    assert isinstance(all_streams, list)
    for stream in all_streams:
        assert isinstance(stream, dict)
        stream_id = stream["id"]
        dump(f"deleting stream {stream_id}")
        result = streams.delete_stream(stream_id)
        assert isinstance(result, dict)
        assert result["id"] == stream_id

    all_streams = streams.get_streams()
    assert isinstance(all_streams, list)
    assert len(all_streams) == 0
