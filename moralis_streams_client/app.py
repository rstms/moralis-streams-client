# webserver subprocess

import logging
import os
import signal
from typing import Dict, List, Optional, Union
from uuid import UUID, uuid4

import orjson
import requests
from fastapi import (
    BackgroundTasks,
    Body,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
    Response,
)
from pydantic import BaseModel, Field
from starlette.middleware import Middleware

from . import settings
from .content_size_limit import ContentSizeLimitMiddleware
from .event_queue import EventQueue
from .signature import Signature
from .validate import validate_signature

logger = logging.getLogger(__name__)

debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical


app = FastAPI(
    middleware=[
        Middleware(
            ContentSizeLimitMiddleware,
            max_content_size=settings.MAX_CONTENT_SIZE,
        )
    ],
    dependencies=[Depends(validate_signature)],
)

# models


class EventQueueFactory:
    events = EventQueue()

    @classmethod
    async def get_events(self):
        return self.events


async def get_event_list():
    return await EventQueueFactory.get_events()


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class VBaseModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

    def dict(self, *args, **kwargs):
        ret = super().dict(*args, **kwargs)
        ret = orjson.loads(orjson_dumps(ret, default=None))
        return ret


class Relay(VBaseModel):
    url: Union[str, None] = Field(..., description="relay target url")
    header: Union[str, None] = Field(
        ..., description="header label for api_key"
    )
    key: Union[str, None] = Field(
        ..., description="relay target api authentication key"
    )


class RelayResponse(VBaseModel):
    result: Relay


class Event(VBaseModel):
    id: UUID = Field(..., description="event id")
    path: str = Field(..., descripton="endpoint path")
    method: str = Field(..., description="HTTP method")
    headers: Dict = Field(..., description="HTTP request headers")
    body: Dict = Field(..., description="body data")
    relay: Optional[Dict] = Field(
        None, description="request return value for forwarded event"
    )


class EventResponse(VBaseModel):
    result: Union[str, Dict, None]


class EventsResponse(VBaseModel):
    result: List[Event]


class MessageResponse(VBaseModel):
    result: Union[str, None]


class BoolResponse(VBaseModel):
    result: bool


class EnableRequest(VBaseModel):
    enable: bool


# helper functions


def header_key(key):
    return "-".join([k.capitalize() for k in key.split("-")])


def obscure_key(key):
    if key is not None:
        key = key[:3] + "...." + key[-3:]
    return key


@app.on_event("startup")
async def startup_event():
    debug(f"{__name__} startup")
    app.state.signature = Signature()
    if not hasattr(app.state, "config"):
        app.state.config = {}
    if not hasattr(app.state, "tunnel_url"):
        app.state.tunnel_url = None
    debug(f"{app.state.config=}")
    debug(f"{app.state.tunnel_url=}")


@app.on_event("shutdown")
async def shutdown_event():
    debug(f"{__name__} shutdown")


@app.get("/hello", response_model=MessageResponse)
async def get_hello():
    return MessageResponse(result="Hello, World!")


# @app.get("/tunnel", response_model=MessageResponse)
@app.get("/tunnel", response_model=MessageResponse)
async def get_tunnel(request: Request):
    tunnel_url = request.app.state.tunnel_url
    return MessageResponse(result=tunnel_url)


@app.post("/buffer", response_model=BoolResponse)
async def post_buffer(
    request: EnableRequest, events: EventQueue = Depends(get_event_list)
):
    events.buffer_enabled = request.enable
    return BoolResponse(result=events.buffer_enabled)


@app.get("/buffer", response_model=BoolResponse)
async def get_buffer(events: EventQueue = Depends(get_event_list)):
    return BoolResponse(result=events.buffer_enabled)


@app.post("/relay", response_model=RelayResponse)
async def post_relay(
    request: Relay, events: EventQueue = Depends(get_event_list)
):
    events.relay_url = request.url
    events.relay_header = request.header
    events.relay_key = request.key

    return RelayResponse(
        result=Relay(
            url=events.relay_url,
            header=events.relay_header,
            key=obscure_key(events.relay_key),
        )
    )


@app.get("/relay", response_model=RelayResponse)
async def get_relay(events: EventQueue = Depends(get_event_list)):
    return RelayResponse(
        result=Relay(
            url=events.relay_url,
            header=events.relay_header,
            key=obscure_key(events.relay_key),
        )
    )


@app.post("/contract/event", response_model=EventResponse)
async def post_contract_event(
    event: Dict, request: Request, events: EventQueue = Depends(get_event_list)
):
    baselen = len(str(request.base_url))

    event = Event(
        id=str(uuid4()),
        path=str(request.url)[baselen:],
        method=request.method,
        headers=dict(request.headers),
        body=event,
    )
    event_id = events.append(event)
    return EventResponse(result=str(event_id))


@app.get("/events", response_model=EventsResponse)
async def get_events(events: EventQueue = Depends(get_event_list)):
    return EventsResponse(result=events.list())


@app.get("/clear", response_model=MessageResponse)
async def get_clear(events: EventQueue = Depends(get_event_list)):
    return MessageResponse(result=events.clear())


@app.get("/event/{event_id}", response_model=EventResponse)
async def get_event(
    response: Response,
    event_id: UUID,
    events: EventQueue = Depends(get_event_list),
):
    event = events.lookup(event_id, delete=False)
    if event is None:
        response.status_code = requests.codes.NOT_FOUND
    return EventResponse(result=event)


@app.delete("/event/{event_id}", response_model=EventResponse)
async def delete_event(
    response: Response,
    event_id: UUID,
    events: EventQueue = Depends(get_event_list),
):
    event = events.lookup(event_id, delete=True)
    if event is None:
        response.status_code = requests.codes.NOT_FOUND
    return EventResponse(result=event)


def reaper():
    os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)


@app.get("/shutdown", response_model=MessageResponse)
async def get_shutdown(background_tasks: BackgroundTasks):
    background_tasks.add_task(reaper)
    return MessageResponse(result="shutdown pending")
