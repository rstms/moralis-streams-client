# test cases for examples from https://github.com/MoralisWeb3/streams-beta#readme

import json
import logging
import time

import pytest
import requests

from moralis_streams_client.webhook import Webhook

WEBHOOK_TIMEOUT = 5


@pytest.fixture(scope="module", autouse=True)
def webhook_process(module_webhook_process):
    yield module_webhook_process


def test_webhook_hello(webhook, dump):
    ret = webhook.hello()
    assert ret == "Hello, World!"
    dump(ret)


def test_webhook_clear(webhook, dump):
    ret = webhook.clear()
    assert ret == "cleared"
    dump(ret)


def test_webhook_events(webhook, dump):
    ret = webhook.events()
    dump(ret)


def test_webhook_queue(webhook, dump, event_keys):
    webhook.clear()
    ret1 = webhook.inject(
        dict(
            int_data=1,
            str_data="some_string_1",
            dict_data={"foo": 1, "bar": 2},
        ),
    )
    assert ret1
    ret2 = webhook.inject(
        dict(
            int_data=2,
            str_data="some_string_2",
            dict_data={"foo": 1, "bar": 2},
        ),
    )
    assert ret2
    ret3 = webhook.inject(
        dict(
            int_data=2,
            str_data="some_string_3",
            dict_data={"foo": 1, "bar": 2},
        ),
    )
    assert ret3
    events = webhook.events()
    assert isinstance(events, list)
    for event in events:
        assert isinstance(event, dict)
        assert set(event.keys()) == set(event_keys)
        dump(event)


def test_webhook_tunnel(
    webhook, webhook_tunnel_url, dump, calculate_signature
):
    webhook.clear()
    url = webhook_tunnel_url + "/contract/event"
    logging.info(f"posting to url {url}")
    payload = {"message": "sent to public url"}
    headers = {
        "X-Signature": calculate_signature(json.dumps(payload).encode())
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.ok
    timeout = time.time() + WEBHOOK_TIMEOUT
    events = []
    while len(events) == 0:
        time.sleep(0.5)
        assert (
            time.time() < timeout
        ), "timeout waiting for webhook event callback"
        events = webhook.events()
        assert isinstance(events, list)
    assert len(events) == 1
    assert events[0]["body"] == payload
    dump(events)
