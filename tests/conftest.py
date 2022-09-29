# common test fixtures

import pytest
import pyngrok
import multiproccesing as mp

SERVER_PORT=8888

class Callback():

    queue = mp.Queue()

    def put(self, item):
        self.queue.put(item)

    def get(self):
        return self.queue.get()

    def list(self):
        items = []
        while not self.queue.empty():
            items.append(self.queue.get())
        return items

    def clear(self):
        while not self.queue.empty():
            self.queue.get() 

    def empty(self):
        return self.queue.empty()

    def size(self):
        return self.queue.qsize()

@pytest.fixture()
def callbacks():
    return Callback()

def webhooker(queue, port):
    from flask import Flask
    import sys
    app = Flask(__name__)

    @app.route("/hello")
    def hello_world():
        print(f"route: /hello")
        return "Hello, World!\n"

    @app.route("/shutdown")
    def shutdown():
        print('shutdown requested')
        sys.exit(0)

    print('starting webhooker...')
    app.run(debug=True, port)
    print('webhooker returned')


@pytest.fixture()
def webhook_server(callbacks):
    try:
        print('webhook_server starting webhooker...')
        p = mp.Process(target=webhooker, args=(callbacks.queue, SERVER_PORT))
        p.start()
        yield p
    finally:
        print('webhook_server killing webhooker...')
        p.kill()
