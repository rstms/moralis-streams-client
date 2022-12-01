# test cases for examples from https://github.com/MoralisWeb3/streams-beta#readme

import json
import logging
import time

import httpx
import pytest

from moralis_streams_client import settings
from moralis_streams_client.signature import Signature
from moralis_streams_client.webhook import Webhook

from .conftest import WebhookServerProcess, is_ok

WEBHOOK_TIMEOUT = 5


@pytest.fixture(scope="module", autouse=True)
async def webhook_process():
    async with WebhookServerProcess() as webhook:
        yield webhook


async def test_webhook_hello(webhook, dump):
    ret = await webhook.hello()
    assert ret == "Hello, Webhook!"
    dump(ret)


async def test_webhook_clear(webhook, dump):
    ret = await webhook.clear()
    assert ret == "cleared"
    dump(ret)


async def test_webhook_events(webhook, dump):
    ret = await webhook.events()
    dump(ret)


async def test_webhook_queue(webhook, dump, event_keys):
    await webhook.clear()
    ret1 = await webhook.inject(
        dict(
            int_data=1,
            str_data="some_string_1",
            dict_data={"foo": 1, "bar": 2},
        ),
    )
    assert ret1
    ret2 = await webhook.inject(
        dict(
            int_data=2,
            str_data="some_string_2",
            dict_data={"foo": 1, "bar": 2},
        ),
    )
    assert ret2
    ret3 = await webhook.inject(
        dict(
            int_data=2,
            str_data="some_string_3",
            dict_data={"foo": 1, "bar": 2},
        ),
    )
    assert ret3
    events = await webhook.events()
    assert isinstance(events, list)
    for event in events:
        assert isinstance(event, dict)
        assert set(event.keys()) == set(event_keys)
        dump(event)


async def test_webhook_tunnel(webhook, webhook_tunnel_url, dump):
    await webhook.clear()
    url = webhook_tunnel_url + "/contract/event"
    logging.info(f"posting to url {url}")
    payload = {"message": "sent to public url"}
    headers = Signature().headers(payload)
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
    assert is_ok(response)
    timeout = time.time() + WEBHOOK_TIMEOUT
    events = []
    while len(events) == 0:
        time.sleep(0.5)
        assert (
            time.time() < timeout
        ), "timeout waiting for webhook event callback"
        events = await webhook.events()
        assert isinstance(events, list)
    assert len(events) == 1
    assert events[0]["body"] == payload
    dump(events)
