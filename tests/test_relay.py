# test relay mode

import atexit
import time
from logging import critical, info
from pathlib import Path
from subprocess import run
from uuid import uuid4

import pytest
from httpx import Headers

from moralis_streams_client import settings
from moralis_streams_client.app import obscure_key
from moralis_streams_client.webhook import Webhook

from .conftest import WebhookServerProcess, wait_for_it

EVENT_COUNT = 10

TEST_RELAY_KEY = "test_relay_key"
RELAY_KEY_HEADER = "X-API-Key"
RELAY_PORT = 8080
TARGET_PORT = 8081


@pytest.fixture(scope="module", autouse=True)
async def webhook_process():
    async with WebhookServerProcess() as webhook:
        yield webhook


@pytest.fixture
def relay_port():
    return RELAY_PORT


@pytest.fixture
def target_port():
    return TARGET_PORT


@pytest.fixture(scope="module")
async def verify_webhook():
    async def _verify_webhook(_webhook, port):
        assert await _webhook.server_running() is True
        procs = await _webhook.processes()
        assert isinstance(procs, list)
        assert len(procs) > 0
        assert _webhook.port == port
        assert await _webhook.clear()
        return True

    return _verify_webhook


@pytest.fixture
def relay_url(target_port):
    return f"http://localhost:{target_port}/contract/event"


@pytest.fixture
def relay_key():
    return TEST_RELAY_KEY


@pytest.fixture
def relay_header():
    return RELAY_KEY_HEADER


@pytest.fixture(scope="module")
async def relay(webhook, verify_webhook):
    """configue running webhook to relay messages to target webhook"""
    relay_port = RELAY_PORT
    target_port = TARGET_PORT
    relay_key = TEST_RELAY_KEY
    relay_header = RELAY_KEY_HEADER
    relay_url = f"http://localhost:{target_port}/contract/event"

    _relay = webhook
    await verify_webhook(_relay, relay_port)
    set_result = await _relay.relay(
        url=relay_url, key=relay_key, header=relay_header
    )
    assert isinstance(set_result, dict)
    get_result = await _relay.relay()
    assert get_result == dict(
        url=relay_url, header=relay_header, key=obscure_key(relay_key)
    )
    try:
        yield _relay
    finally:
        assert await _relay.events() == []
        await _relay.relay(enable=False)
        assert await _relay.relay() == dict(url=None, header=None, key=None)
        assert await _relay.buffer() is True


@pytest.fixture(scope="module")
async def target(verify_webhook):
    target_port = TARGET_PORT
    _target = Webhook(
        debug=True,
        port=target_port,
        tunnel=False,
    )
    log_file = Path(".") / "relay.log"
    await _target.start(wait=True, log_file=str(log_file))
    wait_for_it(_target.addr, _target.port)
    assert await _target.server_running()
    assert await verify_webhook(_target, target_port)
    await _target.relay(enable=False)
    try:
        yield _target
    finally:
        assert await _target.events() == []
        await _target.relay(enable=False)
        assert await _target.relay() == dict(url=None, header=None, key=None)
        assert await _target.buffer() is True
        await _target.stop()


async def test_relay_messages(
    relay, target, relay_url, relay_key, relay_header
):
    assert await relay.clear()
    assert await target.clear()

    assert await relay.relay() == dict(
        url=f"http://localhost:{target.port}/contract/event",
        header=relay_header,
        key=obscure_key(relay_key),
    )
    assert await target.relay() == dict(url=None, header=None, key=None)

    assert len(await target.events()) == 0
    assert len(await relay.events()) == 0

    sent_events = {}
    for i in range(EVENT_COUNT):
        event = dict(test=f"payload_{i}", count=i, id=str(uuid4()))
        event_id = await relay.inject(event)
        sent_events[event_id] = event

    while len(await target.events()) < EVENT_COUNT:
        info(f"target_events_length={target.events()}")
        time.sleep(1)

    target_events = await target.events()

    sent_ids = list(sent_events.keys())
    target_ids = [t["id"] for t in target_events]
    assert len(sent_ids) == len(target_ids)

    for i, sid in enumerate(sent_events.keys()):
        sbody = sent_events[sid]
        tev = target_events[i]
        tbody = tev["body"]
        assert sbody == tbody
        assert isinstance(tev["headers"], dict)
        assert relay_header in Headers(tev["headers"])
        assert Headers(tev["headers"])[relay_header] == relay_key

    for event in target_events:
        event_id = Headers(event["headers"])["x-relay-id"]
        assert await relay.event(event_id)
        await relay.delete(event_id)

    assert await relay.events() == []


async def test_relay_id(
    relay, target, relay_url, relay_key, relay_header, dump
):
    assert await relay.clear()
    assert await target.clear()

    msg_id = str(uuid4())
    event = dict(test="payload", id=msg_id)
    await relay.inject(event)
    tevs = await target.events()
    assert len(tevs) == 1
    dump(tevs[0])
    assert tevs[0]["body"]["id"] == msg_id
    await relay.clear()
    await target.clear()


def _make_huge_event(size):
    msg_id = str(uuid4())
    huge = "a" + "u" * size + "gh"
    event = dict(test="huge", id=msg_id, castle_of=huge)
    return event


async def test_relay_huge(
    relay, target, relay_url, relay_key, relay_header, dump
):
    assert await relay.clear()
    assert await target.clear()

    event = _make_huge_event(8_000_000)

    await relay.inject(event)

    tevs = await target.events()
    assert len(tevs) == 1
    assert tevs[0]["body"]["id"] == event["id"]
    assert len(tevs[0]["body"]["castle_of"]) == len(event["castle_of"])
    await relay.clear()
    await target.clear()


async def test_relay_recover_huge(
    relay, target, relay_url, relay_key, relay_header, dump
):
    assert await relay.clear()
    assert await target.clear()

    event = _make_huge_event(11_000_000)

    with pytest.raises(Exception) as exc:
        await relay.inject(event)
    info(f"Exception: {exc}")

    event = _make_huge_event(9_000_000)
    await relay.inject(event)

    tevs = await target.events()
    assert len(tevs) == 1
    assert tevs[0]["body"]["id"] == event["id"]
    assert len(tevs[0]["body"]["castle_of"]) == len(event["castle_of"])
    await relay.clear()
    await target.clear()
