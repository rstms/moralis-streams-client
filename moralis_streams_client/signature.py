# streams api client wrapper

import os

from eth_hash.auto import keccak
from eth_utils import to_hex


class Signature:
    def __init__(self, api_key=None, header="X-Signature"):
        self.api_key = api_key or os.environ["MORALIS_API_KEY"]
        self.api_key = self.api_key.encode()
        self.header = header

    def validate(self, signature: bytes, body: bytes) -> bool:
        """calculate the sha3 checksum and validate the request"""
        return signature == self.calculate(body)

    def calculate(self, body: bytes) -> bytes:
        """calculate the sha3 checksum of body and api_key"""
        s = keccak.new(body)
        s.update(self.api_key)
        return to_hex(s.digest())

    def headers(self, body: bytes) -> dict:
        return {self.header: self.calculate(body)}
