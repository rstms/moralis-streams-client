from logging import info

import uvicorn

from . import settings
from .app import app
from .tunnel import NgrokTunnel


class ServerProcess:
    def __init__(self, **kwargs):
        self.addr = kwargs.get("addr", settings.ADDR)
        self.port = kwargs.get("port", settings.PORT)
        self.tunnel = kwargs.get("tunnel", settings.TUNNEL)
        self.token = kwargs.get("token", str(settings.NGROK_AUTHTOKEN))
        self.debug = kwargs.get("debug", settings.DEBUG)
        self.log_level = kwargs.get("log_level", settings.LOG_LEVEL)
        self.config = kwargs.get("config", {})
        self.config["tunnel"] = self.tunnel
        self.config["addr"] = self.addr
        self.config["port"] = self.port
        app.state.config = self.config
        app.state.tunnel_url = None

    def run(self):
        def fileConfig(*args, **kwargs):
            info("uvicorn logging config disabled")

        uvicorn.config.logging.config.fileConfig = fileConfig

        def _uvicorn_run():
            return uvicorn.run(
                "moralis_streams_client.app:app",
                host=self.addr,
                port=self.port,
                log_level=self.log_level.lower(),
                log_config="disable",
            )

        if self.tunnel is True:
            print(f"starting ngrok tunnel {self.tunnel=}")
            with NgrokTunnel(self.port, self.token) as tunnel:
                app.state.tunnel_url = tunnel.public_url
                return _uvicorn_run()
        else:
            print(f"ngrok tunnel disabled: {self.tunnel=}")
            return _uvicorn_run()
