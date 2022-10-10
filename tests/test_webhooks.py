# test cases for examples from https://github.com/MoralisWeb3/streams-beta#readme

import json
import logging
import time

import pytest
import requests

WEBHOOK_TIMEOUT = 5


def test_webhook_hello(webhook, dump):
    ret = webhook("hello")
    assert isinstance(ret, dict)
    assert "result" in ret
    dump(ret)


def test_webhook_clear(webhook, dump):
    ret = webhook("clear")
    assert isinstance(ret, dict)
    assert "result" in ret
    dump(ret)


def test_webhook_events(webhook, dump):
    ret = webhook("events")
    assert isinstance(ret["result"], list)
    dump(ret["result"])


def test_webhook_queue(webhook, dump):
    webhook("clear")
    ret1 = webhook(
        "contract/event",
        json_data=dict(
            int_data=1,
            str_data="some_string_1",
            dict_data={"foo": 1, "bar": 2},
        ),
    )
    assert ret1
    ret2 = webhook(
        "contract/event",
        json_data=dict(
            int_data=2,
            str_data="some_string_2",
            dict_data={"foo": 1, "bar": 2},
        ),
    )
    assert ret2
    ret3 = webhook(
        "contract/event",
        json_data=dict(
            int_data=2,
            str_data="some_string_3",
            dict_data={"foo": 1, "bar": 2},
        ),
    )
    assert ret3
    ret = webhook("events")
    events = ret["result"]
    assert isinstance(events, list)
    for event in events:
        assert isinstance(event, dict)
        dump(event)


def test_webhook_tunnel(
    webhook, webhook_tunnel_url, dump, calculate_signature
):
    ret = webhook("clear")
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
        ret = webhook("events")
        assert isinstance(ret, dict)
        events = ret["result"]
        assert isinstance(events, list)
    assert len(events) == 1
    assert events[0]["body"] == payload
    logging.info(events)
