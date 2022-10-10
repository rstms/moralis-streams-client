# ngrok tunnel

import atexit
import logging
import os

from pyngrok import ngrok


class NgrokTunnel:

    tunnel = None

    def __init__(self, port=None, token=None):
        if self.__class__.tunnel is None:
            logging.debug("Connecting ngrok tunnel...")
            token = token or os.environ["NGROK_AUTHTOKEN"]
            ngrok.set_auth_token(token)
            self.__class__.tunnel = ngrok.connect(port)
            logging.debug(f"public_url={self.url()}")

    def __enter__(self):
        return self.tunnel

    def __exit__(self, _, exc, tb):
        if self.tunnel is not None:
            self.disconnect()

    def url(self):
        return self.tunnel.public_url

    def disconnect(self):
        url = self.url()
        logging.debug(f"Disconnecting ngrok tunnel: {url}")
        ngrok.disconnect(url)
        self.__class__.tunnel = None
