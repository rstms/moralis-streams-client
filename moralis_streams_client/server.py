#!/usr/bin/env python3

import logging
import sys

import click
import uvicorn

from moralis_streams_client import settings
from moralis_streams_client.app import app
from moralis_streams_client.logconfig import configure_logging
from moralis_streams_client.tunnel import NgrokTunnel


class ServerProcess:
    def __init__(self, **kwargs):

        self.debug = kwargs.get("debug", settings.DEBUG)
        self.addr = kwargs.get("addr", settings.ADDR)
        self.port = kwargs.get("port", settings.PORT)
        self.tunnel = kwargs.get("tunnel", settings.TUNNEL)
        self.log_level = kwargs.get("log_level", settings.LOG_LEVEL)

        self.config = kwargs.get("config", {})
        self.config["debug"] = settings.DEBUG
        self.config["log_level"] = settings.LOG_LEVEL
        app.state.tunnel_url = None
        app.state.config = self.config

        configure_logging()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(settings.LOG_LEVEL)
        self.info = self.logger.info

    def run(self):
        def fileConfig(*args, **kwargs):
            self.info("uvicorn logging config disabled")

        uvicorn.config.logging.config.fileConfig = fileConfig

        def _uvicorn_run():
            return uvicorn.run(
                "moralis_streams_client.app:app",
                host=self.addr,
                port=self.port,
                log_level=self.log_level.lower(),
                log_config="disable",
            )

        if self.tunnel:
            self.info("starting ngrok tunnel...")
            with NgrokTunnel(
                self.port, str(settings.NGROK_AUTHTOKEN)
            ) as tunnel:
                app.state.tunnel_url = tunnel.public_url
                return _uvicorn_run()
        else:
            self.info("ngrok tunnel disabled")
            return _uvicorn_run()


@click.command
@click.option(
    "-p",
    "--port",
    type=int,
    required=True,
    help="server listen port",
)
def server(port):
    sys.exit(ServerProcess(port=port).run())
