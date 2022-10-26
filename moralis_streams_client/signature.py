# streams api client wrapper

import json
import logging
import os

from eth_hash.auto import keccak
from eth_utils import to_hex

from . import settings

logger = logging.getLogger("signature")
debug = logger.debug
error = logger.error
critical = logger.critical


class Signature:
    def __init__(self, key=None, header="X-Signature"):
        key = key or str(settings.API_KEY)
        self.key = self._bytes(key)
        self.header = header

    def _bytes(self, data):
        if isinstance(data, dict):
            data = json.dumps(data).encode()
        if isinstance(data, str):
            data = data.encode()
        elif not isinstance(data, bytes):
            raise TypeError()
        return data

    def validate(self, signature: bytes, body: bytes) -> bool:
        """calculate the sha3 checksum and validate the request"""
        valid = signature == self.calculate(body)
        return valid

    def calculate(self, body: bytes) -> bytes:
        """calculate the sha3 checksum of body and api_key"""
        body = self._bytes(body)
        debug(f"calculate: {len(body)} bytes")
        body = self._bytes(body)
        s = keccak.new(body)
        s.update(self.key)
        ret = to_hex(s.digest())
        debug(f"{ret=}")
        return ret

    def headers(self, body: bytes) -> dict:
        return {self.header: self.calculate(body)}
