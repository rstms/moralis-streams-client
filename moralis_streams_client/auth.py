# signature checksum verification

from eth_hash.auto import keccak
from eth_utils import to_hex


def verify_signature(signature, body, key):
    """calculate the sha3 checksum to validate the request"""
    s = keccak.new(body)
    s.update(key)
    calculated = to_hex(s.digest())
    return calculated == signature
