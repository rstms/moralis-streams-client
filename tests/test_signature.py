# signature tests

import json

import pytest

from moralis_streams_client.signature import Signature


@pytest.fixture
def testdata():
    return dict(
        parrot=dict(breed="norweigan blue", status="pining for the fjords")
    )


@pytest.fixture
def testbytes(testdata):
    return json.dumps(testdata).encode()


@pytest.fixture
def testkey():
    return "this_parrot_has_ceased_to_be".encode()


@pytest.fixture
def testheader():
    return "X-Parrot-Test"


@pytest.fixture
def badbytes():
    return "and_now_for_something_completely_different".encode()


def test_signature_defaults(testkey):
    s = Signature(testkey)
    assert s.key == testkey
    assert s.header.startswith("X-")


def test_signature_validation(testkey, testbytes, badbytes):
    s = Signature(testkey)
    sig = s.calculate(testbytes)
    valid = s.validate(sig, testbytes)
    assert valid is True
    invalid_data = s.validate(sig, badbytes)
    assert invalid_data is False
    invalid_key = s.validate(badbytes, testbytes)
    assert invalid_key is False
    valid_again = s.validate(sig, testbytes)
    assert valid_again is True


def test_signature_headers(testkey, testheader, testbytes):
    s = Signature(testkey, testheader)
    sig = s.calculate(testbytes)
    headers = s.headers(testbytes)
    assert headers == {testheader: sig}
    valid = s.validate(headers[testheader], testbytes)
    assert valid is True


def test_signature_str_key(testbytes):
    testkey = "dimsdale"
    s = Signature(testkey)
    sig = s.calculate(testbytes)
    valid = s.validate(sig, testbytes)
    assert valid is True


def test_signature_str_sig(testbytes):
    testkey = "a_lupin"
    s = Signature(testkey)
    sig = s.calculate(testbytes)
    assert isinstance(sig, str)
    assert s.validate(sig, testbytes)
    assert not s.validate("completely_different", testbytes)
