# common test fixtures

import multiprocessing as mp
import queue
from time import sleep

import attr
import pyngrok
import pytest

SERVER_PORT = 8888
QSIZE = 1024


@pytest.fixture
def server_port():
    return SERVER_PORT


@attr.s(auto_attribs=True)
class Callback:

    queue = mp.Queue(QSIZE)

    def put(self, item):
        self.queue.put(item, False)
        while self.empty() is True or self.size() < 1:
            sleep(0.001)

    def get(self, block=True, timeout=None):
        return self.queue.get(block, timeout)

    def list(self, block=True, timeout=None, sentinel=None, count=None):
        items = []
        # print(f"list_enter {self} q_size={self.queue.qsize()} q_empty={self.queue.empty()} items={len(items)}")
        while True:
            try:
                item = self.queue.get(block, timeout)
            except queue.Empty:
                break
            items.append(item)
            if sentinel is not None and item == sentinel:
                break
            if count is not None and len(items) >= count:
                break
        return items

    def clear(self):
        try:
            while not self.empty():
                self.get(False)
        except queue.Empty:
            pass

    def empty(self):
        return self.queue.empty()

    def size(self):
        return self.queue.qsize()


@pytest.fixture()
def callbacks():
    try:
        cb = Callback()
        # print(f"callbacks: yielding {cb} {cb.queue}")
        yield cb
    finally:
        pass
        # print(f"callbacks: releasing {cb} {cb.queue}")


def webhooker(queue, port):
    import sys

    from flask import Flask

    print(f"webhooker startup: {queue=} {port=}")

    app = Flask(__name__)

    @app.route("/hello")
    def hello_world():
        print("route: /hello")
        return "Hello, World!\n"

    @app.route("/shutdown")
    def shutdown():
        print("shutdown requested")
        sys.exit(0)

    print("calling webhooker run...")
    app.run(debug=True, port=port)
    print("webhooker run returned")


@pytest.fixture(scope="session", autouse=True)
def webhook_server(k):
    try:
        print("webhook_server starting webhooker...")
        p = mp.Process(target=webhooker, args=(Callback.queue, SERVER_PORT))
        p.start()
        yield p
    finally:
        print("webhook_server killing webhooker...")
        p.kill()
