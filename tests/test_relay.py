# test relay mode

import atexit
import time
from logging import critical, info
from pathlib import Path
from subprocess import run
from uuid import uuid4

import pytest
from requests.structures import CaseInsensitiveDict as Headers

from moralis_streams_client import settings
from moralis_streams_client.app import obscure_key
from moralis_streams_client.webhook import Webhook

EVENT_COUNT = 10

TEST_RELAY_KEY = "test_relay_key"
RELAY_KEY_HEADER = "X-API-Key"
RELAY_PORT = 8080
TARGET_PORT = 8081


@pytest.fixture(scope="module", autouse=True)
def webhook_process(module_webhook_process):
    yield module_webhook_process


@pytest.fixture
def relay_port():
    return RELAY_PORT


@pytest.fixture
def target_port():
    return TARGET_PORT


@pytest.fixture(scope="module")
def verify_webhook():
    def _verify_webhook(_webhook, port):
        assert _webhook.server_running() is True
        procs = _webhook.processes()
        assert isinstance(procs, list)
        assert len(procs) > 0
        assert _webhook.port == port
        assert _webhook.clear()
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
def relay(webhook, verify_webhook):
    """configue running webhook to relay messages to target webhook"""
    relay_port = RELAY_PORT
    target_port = TARGET_PORT
    relay_key = TEST_RELAY_KEY
    relay_header = RELAY_KEY_HEADER
    relay_url = f"http://localhost:{target_port}/contract/event"

    _relay = webhook
    verify_webhook(_relay, relay_port)
    set_result = _relay.relay(
        url=relay_url, key=relay_key, header=relay_header
    )
    assert isinstance(set_result, dict)
    get_result = _relay.relay()
    assert get_result == dict(
        url=relay_url, header=relay_header, key=obscure_key(relay_key)
    )
    try:
        yield _relay
    finally:
        assert _relay.events() == []
        _relay.relay(enable=False)
        assert _relay.relay() == dict(url=None, header=None, key=None)
        assert _relay.buffer() is True


@pytest.fixture(scope="module")
def target(wait_for_it, verify_webhook):
    target_port = TARGET_PORT
    _target = Webhook(
        debug=True,
        port=target_port,
        tunnel=False,
    )
    logfile = Path(".") / "relay.log"
    _target.start(wait=True, logfile=str(logfile))
    wait_for_it(_target.addr, _target.port)
    assert _target.server_running()
    assert verify_webhook(_target, target_port)
    _target.relay(enable=False)
    try:
        yield _target
    finally:
        assert _target.events() == []
        _target.relay(enable=False)
        assert _target.relay() == dict(url=None, header=None, key=None)
        assert _target.buffer() is True
        _target.stop()


def test_relay_messages(relay, target, relay_url, relay_key, relay_header):
    assert relay.clear()
    assert target.clear()

    assert relay.relay() == dict(
        url=f"http://localhost:{target.port}/contract/event",
        header=relay_header,
        key=obscure_key(relay_key),
    )
    assert target.relay() == dict(url=None, header=None, key=None)

    assert len(target.events()) == 0
    assert len(relay.events()) == 0

    sent_events = {}
    for i in range(EVENT_COUNT):
        event = dict(test=f"payload_{i}", count=i, id=str(uuid4()))
        event_id = relay.inject(event)
        sent_events[event_id] = event

    while len(target.events()) < EVENT_COUNT:
        info(f"target_events_length={target.events()}")
        time.sleep(1)

    target_events = target.events()

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
        assert relay.event(event_id)
        relay.delete(event_id)

    assert relay.events() == []


def test_relay_id(relay, target, relay_url, relay_key, relay_header, dump):
    assert relay.clear()
    assert target.clear()

    msg_id = str(uuid4())
    event = dict(test="payload", id=msg_id)
    relay.inject(event)
    tevs = target.events()
    assert len(tevs) == 1
    dump(tevs[0])
    assert tevs[0]["body"]["id"] == msg_id
    relay.clear()
    target.clear()


def _make_huge_event(size):
    msg_id = str(uuid4())
    huge = "a" + "u" * size + "gh"
    event = dict(test="huge", id=msg_id, castle_of=huge)
    return event


def test_relay_huge(relay, target, relay_url, relay_key, relay_header, dump):
    assert relay.clear()
    assert target.clear()

    event = _make_huge_event(8_000_000)

    relay.inject(event)

    tevs = target.events()
    assert len(tevs) == 1
    assert tevs[0]["body"]["id"] == event["id"]
    assert len(tevs[0]["body"]["castle_of"]) == len(event["castle_of"])
    relay.clear()
    target.clear()


def test_relay_recover_huge(
    relay, target, relay_url, relay_key, relay_header, dump
):
    assert relay.clear()
    assert target.clear()

    event = _make_huge_event(11_000_000)

    with pytest.raises(Exception) as exc:
        relay.inject(event)
    info(f"Exception: {exc}")

    event = _make_huge_event(9_000_000)
    relay.inject(event)

    tevs = target.events()
    assert len(tevs) == 1
    assert tevs[0]["body"]["id"] == event["id"]
    assert len(tevs[0]["body"]["castle_of"]) == len(event["castle_of"])
    relay.clear()
    target.clear()
