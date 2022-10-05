# api tests

import os
from logging import info
from pathlib import Path

import ape
import MoralisSDK.api
import pytest
import yaml
from backoff import expo, on_exception
from box import Box
from eth_utils import event_abi_to_log_topic, to_checksum_address
from ratelimit import RateLimitException, limits

from moralis_streams_client.api import connect

CHAIN_ID = "0x5"

ECOSYSTEM = "ethereum"
NETWORK = "goerli"
PROVIDER = "alchemy"

ETHERSCAN_LIMIT_COUNT = 5
ETHERSCAN_LIMIT_SECONDS = 1

EVENT_NAME = "PrintMintPending"


@pytest.fixture
def config():
    def _config(key):
        return os.environ[key]

    return _config


@pytest.fixture
def api(config):
    key = config("MORALIS_API_KEY")
    return connect(key=key, format_dict=True)


@pytest.fixture
def explorer():
    selector = f"{ECOSYSTEM}:{NETWORK}:{PROVIDER}"
    assert selector in list(ape.networks.get_network_choices())
    with ape.networks.parse_network_choice(selector) as network:
        yield network.network.explorer


@pytest.fixture
def system_address(config):
    address = config("TEST_SYSTEM_ADDRESS")
    return to_checksum_address(address)


@pytest.fixture
def user_address(config):
    address = config("TEST_USER_ADDRESS")
    return to_checksum_address(address)


@pytest.fixture
def test_ethersieve_contract(config):
    address = config("TEST_ETHERSIEVE_CONTRACT")
    return to_checksum_address(address)


@pytest.fixture
def test_background_contract(config):
    address = config("TEST_BACKGROUND_CONTRACT")
    return to_checksum_address(address)


@pytest.fixture
def moralis(config):
    api = MoralisSDK.api.MoralisApi()
    api.set_api_key(config("MORALIS_API_KEY"))
    return api


# rate-limit etherscan api calls
@on_exception(expo, RateLimitException, max_tries=16)
@limits(calls=ETHERSCAN_LIMIT_COUNT, period=ETHERSCAN_LIMIT_SECONDS)
def limit(func, *args, **kwargs):
    return func(*args, **kwargs)


def test_transactions(explorer, system_address, moralis):
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
        abi = limit(explorer.get_contract_type, addr)
        contract = ape.contracts.ContractInstance(addr, abi)
        info(f"{contract.symbol()} {contract}")
        url = explorer.get_address_url(addr)
        info(url)
        token_ids = Box(moralis.get_token_id(addr, chain="goerli"))
        info(f"  tokens={int(token_ids.total)}")
        owners = Box(moralis.get_nft_owners(addr, chain="goerli"))
        assert token_ids.total == owners.total
        for owner in owners.result:
            info(f"  {int(owner.token_id)}: {owner.name} {owner.owner_of}")


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


def test_api_get_stats(api, dump):
    ret = api.get_stats()
    assert isinstance(ret, dict)
    dump(ret)


def test_api_create_stream(
    api, dump, test_ethersieve_contract, explorer, webhook, webhook_tunnel_url
):

    contract_type = limit(explorer.get_contract_type, test_ethersieve_contract)
    contract = ape.contracts.ContractInstance(
        test_ethersieve_contract, contract_type
    )

    event_abi = contract_type.events[EVENT_NAME].dict()
    event_topic = event_abi_to_log_topic(event_abi)

    ret = api.create_stream(
        webhook_url=webhook_tunnel_url + "/contract/event",
        description="moralis_streams_client testing stream",
        tag="msc_test",
        chain_ids=[CHAIN_ID],
        stream_type="contract",
        address=test_ethersieve_contract,
        topic=event_topic,
        include_native_txs=False,
        abi=event_abi,
        filter_=None,
    )
    assert isinstance(ret, dict)
    dump(ret)
    breakpoint()
    pass
