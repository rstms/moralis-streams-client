# server tests

import json
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient

from moralis_streams_client import settings
from moralis_streams_client.app import app, obscure_key
from moralis_streams_client.signature import Signature


@pytest.fixture
async def client(webhook_process):
    async with AsyncClient(app=app, base_url="http://test") as client:
        for event in app.router.on_startup:
            await event()
        try:
            yield client
        finally:
            for event in app.router.on_shutdown:
                await event()


@pytest.fixture
def signature():
    key = str(settings.API_KEY)
    return Signature(key)


@pytest.fixture
async def _do_request(client, signature):
    async def _do_request(
        method, path, headers={}, data={}, expect_status=200
    ):
        headers.update(signature.headers(data))
        response = await client.request(
            method, path, headers=headers, json=data
        )
        assert response.status_code == expect_status
        response_dict = response.json()
        if response.is_success:
            assert isinstance(response_dict, dict)
            assert set(response_dict.keys()) == set(["result"])
            result = response_dict["result"]
        else:
            result = response_dict
        return result

    assert await _do_request("GET", "clear", {}, {}) == "cleared"

    return _do_request


@pytest.fixture
def get(_do_request):
    async def _get(path, **kwargs):
        return await _do_request("GET", path, **kwargs)

    return _get


@pytest.fixture
def post(_do_request, get):
    async def _post(path, **kwargs):
        return await _do_request("POST", path, **kwargs)

    return _post


@pytest.fixture
def delete(_do_request, get):
    async def _delete(path, **kwargs):
        return await _do_request("DELETE", path, **kwargs)

    return _delete


async def test_server_hello(get):
    result = await get("hello")
    assert result == "Hello, Webhook!"


async def test_server_tunnel(get):
    result = await get("tunnel")
    assert result is None


async def test_server_buffer(post, get):
    assert await get("buffer") is True
    assert await post("buffer", data=dict(enable=False)) is False
    assert await get("buffer") is False
    assert await post("buffer", data=dict(enable=True)) is True
    assert await get("buffer") is True


def _obscured(relay):
    ret = {}
    for k, v in relay.items():
        if k == "key":
            if v is not None:
                v = obscure_key(v)
        ret[k] = v
    return ret


async def test_server_relay(get, post):
    default_relay = dict(
        url=settings.RELAY_URL,
        header=settings.RELAY_HEADER,
        key=str(settings.RELAY_KEY),
    )

    test_relay = dict(
        url="http://howdy/howdy/howdy",
        header="x-crazy-header",
        key="when-you-can-snatch-the-pebble-from-my-hand",
    )

    null_relay = dict(url=None, header=None, key=None)

    response = await get("relay")
    assert response == _obscured(default_relay)

    response = await post("relay", data=test_relay)
    assert response == _obscured(test_relay)

    response = await post("relay", data=null_relay)
    assert response == null_relay

    response = await post("relay", data=default_relay)
    assert response == _obscured(default_relay)


@pytest.fixture
def testevent():
    return dict(
        id=str(uuid4()),
        kniggits=["robin", "bedeveire", "lancelot"],
        swallows=["african", "european"],
        data=[dict(id=str(uuid4()), sketch="confuse-a-cat")],
        more_data=dict(foo=dict(id=str(uuid4())), id=str(uuid4())),
        grip_method="by the husk",
    )


async def test_server_contract_event(get, post, testevent):
    assert await get("events") == []
    eid = await post("contract/event", data=testevent)
    assert UUID(eid)
    events = await get("events")
    assert len(events) == 1
    assert events[0]["id"] == eid


async def test_server_events(get, post, testevent):
    assert await get("events") == []
    eid1 = await post("contract/event", data=testevent)
    assert UUID(eid1)
    eid2 = await post("contract/event", data=testevent)
    assert UUID(eid2)
    eid3 = await post("contract/event", data=testevent)
    assert UUID(eid3)
    events = await get("events")
    assert isinstance(events, list)
    assert len(events) == 3
    for event in events:
        assert isinstance(event, dict)
        assert UUID(event["id"])


async def test_server_clear(get):
    result = await get("clear")
    assert result == "cleared"


async def test_server_get_event(get, post, testevent):
    assert await get("events") == []
    event_id = await post("contract/event", data=testevent)
    assert UUID(event_id)
    event = await get(f"event/{event_id}")
    assert event["body"] == testevent
    not_found = await get("events/blarg", expect_status=404)
    assert isinstance(not_found, dict)
    assert "result" not in not_found


async def test_server_delete_event(get, post, delete, testevent):
    assert await get("events") == []
    event_id = await post("contract/event", data=testevent)
    assert UUID(event_id)
    events = await get("events")
    assert len(events) == 1
    assert event_id == events[0]["id"]
    deleted_event = await delete(f"event/{event_id}")
    assert deleted_event["body"] == testevent
    events = await get("events")
    assert events == []


async def test_server_send_relay(get, post, testevent, webhook_process_class):
    async with webhook_process_class(
        port=8081, tunnel=False, log_file="target.log"
    ) as target:
        assert await target.server_running()
        assert await target.clear() == "cleared"
        assert await target.events() == []
        relay_config = dict(
            url="http://localhost:8081/contract/event",
            header="X-API-Key",
            key="test_server_send_relay",
        )
        ret = await post("relay", data=relay_config)
        assert ret["url"] == relay_config["url"]
        event_id = await post("contract/event", data=testevent)

        sent_events = await get("events")
        assert len(sent_events) == 1
        assert sent_events[0]["id"] == event_id
        assert sent_events[0]["relay"]

        events = await target.events()
        assert len(events) == 1
        assert events[0]["headers"]["x-relay-id"] == event_id
        assert events[0]["headers"]["x-api-key"] == relay_config["key"]
        assert events[0]["body"] == testevent
