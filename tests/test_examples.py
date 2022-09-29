# test cases for examples from https://github.com/MoralisWeb3/streams-beta#readme

import pytest
from subprocess import Popen

@pytest.fixture()
def callbacks():
    yield list()

@pytest.fixture()
def catcher(callbacks):
    class Receiver():
        Popen('ngrok')
        catcherreceiver()
    clas


