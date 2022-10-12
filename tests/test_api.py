# api tests

import os
import time
from logging import debug, info
from pathlib import Path

import ape
import MoralisSDK.api
import pytest
import yaml
from backoff import expo, on_exception
from box import Box, BoxList
from eth_utils import (
    event_abi_to_log_topic,
    is_same_address,
    to_checksum_address,
    to_hex,
)
from ratelimit import RateLimitException, limits

import moralis_streams_client

CHAIN_ID = "0x5"

ECOSYSTEM = "ethereum"
NETWORK = "goerli"
PROVIDER = "alchemy"

ETHERSCAN_LIMIT_COUNT = 5
ETHERSCAN_LIMIT_SECONDS = 1

EVENT_NAME = "PrintMintPending"
CONFIRM_COUNT = 12

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
def explorer(ecosystem, network, provider):
    selector = f"{ecosystem}:{network}:{provider}"
    assert selector in list(ape.networks.get_network_choices())
    with ape.networks.parse_network_choice(selector) as network:
        yield network.network.explorer


@pytest.fixture
def system_address(config):
    address = config("TEST_SYSTEM_ADDRESS")
    return to_checksum_address(address)


@pytest.fixture
def system_key(config):
    return config("TEST_SYSTEM_KEY")


@pytest.fixture
def system_passphrase(config):
    return config("TEST_SYSTEM_PASSPHRASE")


@pytest.fixture
def user_address(config):
    address = config("TEST_USER_ADDRESS")
    return to_checksum_address(address)


@pytest.fixture
def user_key(config):
    return config("TEST_USER_KEY")


@pytest.fixture
def user_passphrase(config):
    return config("TEST_USER_PASSPHRASE")


@pytest.fixture
def ethersieve_contract_address(config):
    address = config("TEST_ETHERSIEVE_CONTRACT")
    return to_checksum_address(address)


@pytest.fixture
def event_name():
    return EVENT_NAME


@pytest.fixture
def background_contract_address(config):
    address = config("TEST_BACKGROUND_CONTRACT")
    return to_checksum_address(address)


@pytest.fixture
def moralis(config):
    api = MoralisSDK.api.MoralisApi()
    api.set_api_key(config("MORALIS_API_KEY"))
    return api


@pytest.fixture
def get_contract(explorer):
    def _get_contract(address):
        contract_type = limit(explorer.get_contract_type, address)
        contract = ape.contracts.ContractInstance(address, contract_type)
        assert contract
        return contract

    return _get_contract


# rate-limit etherscan api calls
@on_exception(expo, RateLimitException, max_tries=16)
@limits(calls=ETHERSCAN_LIMIT_COUNT, period=ETHERSCAN_LIMIT_SECONDS)
def limit(func, *args, **kwargs):
    return func(*args, **kwargs)


@pytest.fixture
def get_contract_tokens(explorer, moralis, network):
    def _get_contract_tokens(contract_address):
        owners = Box(moralis.get_nft_owners(contract_address, chain=network))
        assert "result" in owners
        return owners.result

    return _get_contract_tokens


def test_transactions(
    explorer, get_contract, get_contract_tokens, system_address, moralis
):
    assert explorer
    txns = list(limit(explorer.get_account_transactions, system_address))
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
        contract = get_contract(addr)
        info(f"{contract.symbol()} {contract}")

        url = explorer.get_address_url(addr)
        info(url)

        token_ids = Box(moralis.get_token_id(addr, chain="goerli"))
        info(f"  tokens={int(token_ids.total)}")

        tokens = get_contract_tokens(addr)
        assert token_ids.total == len(tokens)
        for token in tokens:
            info(f"  {int(token.token_id)}: {token.name} {token.owner_of}")


def test_moralis_api(moralis, system_address, user_address):
    info(f"{system_address=}")
    system_nfts = Box(moralis.get_nfts(system_address, chain="goerli"))
    for nft in system_nfts.result:
        info(
            f"{nft.symbol} {int(nft.token_id)} {nft.name} mint_block={nft.block_number_minted} contract={nft.token_address}"
        )

    info(f"{user_address=}")
    user_nfts = Box(moralis.get_nfts(user_address, chain="goerli"))
    for nft in user_nfts.result:
        info(
            f"{nft.symbol} {int(nft.token_id)} {nft.name} mint_block={nft.block_number_minted} contract={nft.token_address}"
        )


def test_api_get_stats(streams_api, dump):
    ret = streams_api.get_stats()
    assert isinstance(ret, dict)
    dump(ret)


@pytest.fixture
def ethersieve_contract(get_contract, ethersieve_contract_address):
    return get_contract(ethersieve_contract_address)


@pytest.fixture
def background_contract(get_contract, background_contract_address):
    return get_contract(background_contract_address)


def test_api_create_stream(
    streams_api,
    dump,
    chain_id,
    ethersieve_contract,
    background_contract,
    event_name,
    get_contract_tokens,
    system_address,
    system_key,
    system_passphrase,
    user_address,
    user_key,
    user_passphrase,
    explorer,
    webhook,
    webhook_tunnel_url,
):
    webhook("clear")

    streams_begin = streams_api.get_streams()

    event_abi = ethersieve_contract.contract_type.events[event_name].dict()
    event_topic = to_hex(event_abi_to_log_topic(event_abi))
    contract_abi = ethersieve_contract.contract_type.dict()["abi"]

    stream = Box(
        streams_api.create_stream(
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
    assert isinstance(stream, dict)
    dump(f"{stream.id=}")
    dump(f"{stream.tag=}")
    dump(f"{stream.status=}")
    dump(f"{stream.statusMessage=}")

    address_added = Box(
        streams_api.add_address_to_stream(
            stream.id, [ethersieve_contract.address]
        )
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
    provider = explorer.provider
    user = provider.account_manager.load("user")
    user.set_autosign(True, passphrase=user_passphrase)
    user.unlock(user_passphrase)

    """
    txn = ethersieve_contract.printMint.as_transaction(
        0, 0, 1, 2, 3, value="14000000 gwei", sender=user_address,max_fee_per_gas=provider.base_fee
    )
    nonce = provider.get_nonce(user_address)
    txn.nonce = nonce
    signature = user.sign_transaction(txn)
    txn.signature = signature
    txn.required_confirmations = CONFIRM_COUNT
    receipt = provider.send_transaction(txn)
    """
    receipt = ethersieve_contract.printMint(
        0,
        0,
        1,
        2,
        3,
        value="14000000 gwei",
        sender=user,
        max_fee_per_gas=provider.base_fee + 10_000_000_000,
        required_confirmations=CONFIRM_COUNT,
    )
    dump(dict(txn_hash=receipt.txn_hash, status=str(receipt.status)))

    confirmed_height = receipt.block_number + CONFIRM_COUNT
    last_height = receipt.block_number
    info(f"Waiting for {CONFIRM_COUNT} confirmations...")
    count = 1
    while last_height < confirmed_height:
        height = explorer.network.provider.chain_manager.blocks.height
        if last_height != height:
            info(f"block[{count} of {CONFIRM_COUNT}]: {height}")
            last_height = height
            count += 1

    timeout = time.time() + CALLBACK_TIMEOUT
    info(f"Waiting up to {CALLBACK_TIMEOUT} seconds for 3 callback events...")
    events = []
    while len(events) < 3:
        webhook_events = webhook("events")
        events = webhook_events["result"]
        assert time.time() < timeout, "timeout waiting for 3 callback events"
        time.sleep(1)

    assert isinstance(events, list)
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

    result = Box(streams_api.delete_stream(stream.id))
    assert result.id == stream.id

    streams_end = streams_api.get_streams()

    assert len(streams_begin) == len(streams_end)


def test_api_get_streams_default(streams_api):
    streams = streams_api.get_streams()
    assert isinstance(streams, list)
    for i, stream in enumerate(streams):
        assert isinstance(stream, dict)
        info(f"{i}: {stream['id']}")


@pytest.mark.skip(reason="paged_results seem to be broken; revisit later")
def test_api_get_streams_row_limit(streams_api, monkeypatch):
    monkeypatch.setattr(streams_api, "row_limit", 3)
    streams = streams_api.get_streams()
    assert isinstance(streams, list)
    for i, stream in enumerate(streams):
        assert isinstance(stream, dict)
        info(f"{i}: {stream['id']}")


@pytest.mark.skip(reason="paged_results seem to be broken; revisit later")
def test_api_get_streams_row_page_limit(streams_api, monkeypatch):
    monkeypatch.setattr(streams_api, "row_limit", 2)
    monkeypatch.setattr(streams_api, "page_limit", 2)
    streams = streams_api.get_streams()
    assert isinstance(streams, list)
    for i, stream in enumerate(streams):
        assert isinstance(stream, dict)
        info(f"{i}: {stream['id']}")


def test_api_get_history_default(streams_api):
    history_events = streams_api.get_history()
    assert isinstance(history_events, list)
    for i, history_event in enumerate(history_events):
        assert isinstance(history_event, dict)
        info(f"{i}: {history_event['id']}")


@pytest.mark.skip(reason="paged_results seem to be broken; revisit later")
def test_api_get_history_row_limit(streams_api, monkeypatch):
    monkeypatch.setattr(streams_api, "row_limit", 3)
    history_events = streams_api.get_history()
    assert isinstance(history_events, list)
    for i, history_event in enumerate(history_events):
        assert isinstance(history_event, dict)
        info(f"{i}: {history_event['id']}")


@pytest.mark.skip(reason="paged_results seem to be broken; revisit later")
def test_api_get_history_row_page_limit(streams_api, monkeypatch):
    monkeypatch.setattr(streams_api, "row_limit", 3)
    monkeypatch.setattr(streams_api, "page_limit", 2)
    history_events = streams_api.get_history()
    assert isinstance(history_events, list)
    for i, history_event in enumerate(history_events):
        assert isinstance(history_event, dict)
        info(f"{i}: {history_event['id']}")


def test_api_delete_all_streams(streams_api, dump):
    streams = streams_api.get_streams()
    assert isinstance(streams, list)
    for stream in streams:
        assert isinstance(stream, dict)
        stream_id = stream["id"]
        dump(f"deleting stream {stream_id}")
        result = streams_api.delete_stream(stream_id)
        assert isinstance(result, dict)
        assert result["id"] == stream_id

    streams = streams_api.get_streams()
    assert isinstance(streams, list)
    assert len(streams) == 0
