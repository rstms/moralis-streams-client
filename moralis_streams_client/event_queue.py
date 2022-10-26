import collections

import requests
from requests.structures import CaseInsensitiveDict

from . import defaults, settings


class EventQueue:
    def __init__(self):
        self.events = collections.deque([])
        self.buffer_enabled = settings.BUFFER_ENABLE
        self.relay_url = settings.RELAY_URL
        self.relay_header = settings.RELAY_HEADER
        self.relay_key = str(settings.RELAY_KEY)
        self.relay_id_header = settings.RELAY_ID_HEADER

    def append(self, event):
        if self.relay_url:
            _response = self.forward(event)
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

    def forward(self, event):
        headers = event.headers
        if self.relay_header and self.relay_key:
            headers[self.relay_header] = self.relay_key
        headers[self.relay_id_header] = str(event.id)
        return requests.post(self.relay_url, headers=headers, json=event.body)

    def list(self):
        # create a list from the event_queue, preserving order
        ret = []
        tq = self.events.copy()
        try:
            while True:
                ret.append(tq.popleft())
        except IndexError:
            pass
        return ret

    def clear(self):
        self.events.clear()
        return "cleared"

    def lookup(self, event_id, delete):
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
