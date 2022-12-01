import collections
import logging

import httpx

from . import defaults, settings

logger = logging.getLogger(__name__)
debug = logger.debug
logger.setLevel(settings.LOG_LEVEL)


class EventQueue:
    def __init__(self):
        debug("init")
        self.events = collections.deque([])
        self.buffer_enabled = settings.BUFFER_ENABLE
        self.relay_url = settings.RELAY_URL
        self.relay_header = settings.RELAY_HEADER
        self.relay_key = str(settings.RELAY_KEY)
        self.relay_id_header = settings.RELAY_ID_HEADER

    async def append(self, event):
        debug("append")
        if self.relay_url:
            _response = await self.forward(event)
            event.relay = dict(
                url=_response.url,
                status_code=_response.status_code,
                text=_response.text,
                headers=dict(_response.headers),
            )
        else:
            event.relay = None
        if self.buffer_enabled:
            self.events.append(event)
        return event.id

    async def forward(self, event):
        debug("forward")
        headers = event.headers
        if self.relay_header and self.relay_key:
            headers[self.relay_header] = self.relay_key
        headers[self.relay_id_header] = str(event.id)
        debug(f"post({self.relay_url} {headers} {event.body})")
        async with httpx.AsyncClient() as client:
            ret = await client.post(
                self.relay_url, headers=headers, json=event.body
            )
        debug(f"ret={ret}")
        return ret

    async def list(self):
        # create a list from the event_queue, preserving order
        debug("list")
        ret = []
        tq = self.events.copy()
        try:
            while True:
                ret.append(tq.popleft())
        except IndexError:
            pass
        return ret

    async def clear(self):
        debug("clear")
        self.events.clear()
        return "cleared"

    async def lookup(self, event_id, delete):
        debug("lookup")
        tq = self.events.copy()
        if delete:
            self.events.clear()
        found = None
        while True:
            try:
                event = tq.popleft()
                if event.id == event_id:
                    found = event
                    if delete is False:
                        break
                elif delete is True:
                    self.events.append(event)
            except IndexError:
                break

        return found
