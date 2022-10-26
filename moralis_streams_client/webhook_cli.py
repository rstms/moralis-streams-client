# webhook server process

import json
import logging
import os
import sys
from pathlib import Path
from subprocess import CalledProcessError, check_output

import click
import requests
from eth_hash.auto import keccak
from eth_utils import to_hex

from . import settings
from .exception_handler import ExceptionHandler
from .signature import Signature
from .webhook import Webhook

logger = logging.getLogger(__name__)
debug = logger.debug


def output(
    data,
):
    click.echo(json.dumps(data, indent=2))


def fail(error):
    click.echo(f"Error: {error}", err=True)
    sys.exit(-1)


def run(cmd):
    return check_output(cmd, shell=True).decode()


@click.group
@click.option(
    "-a",
    "--addr",
    type=str,
    envvar="WEBHOOK_SERVER_ADDR",
    default="0.0.0.0",
    show_default=True,
    show_envvar=True,
    help="server listen IP addr",
)
@click.option(
    "-p",
    "--port",
    type=int,
    envvar="WEBHOOK_SERVER_PORT",
    show_default=True,
    default=8080,
    show_envvar=True,
    help="server listen port",
)
@click.option(
    "-t/-T",
    "--tunnel/--no-tunnel",
    is_flag=True,
    default=True,
    help="enable / disable ngrok tunnel",
)
@click.option(
    "-r",
    "--relay-url",
    type=str,
    envvar="WEBHOOK_RELAY_URL",
    show_envvar=True,
    help="enable relay to URL",
)
@click.option(
    "-k",
    "--relay-key",
    type=str,
    envvar="WEBHOOK_RELAY_KEY",
    show_envvar=True,
    help="relay API key",
)
@click.option(
    "-h",
    "--relay-header",
    type=str,
    envvar="WEBHOOK_RELAY_HEADER",
    show_envvar=True,
    help="header name for relay API key",
)
@click.option(
    "-b/-B",
    "--enable-buffer/--disable-buffer",
    is_flag=True,
    default=True,
    help="enable/disable event buffer",
)
@click.option(
    "-m",
    "--moralis-api-key",
    type=str,
    envvar="MORALIS_API_KEY",
    show_envvar=True,
    help="Moralis Streams API key",
)
@click.option("-d", "--debug", is_flag=True)
@click.option(
    "-l",
    "--log-level",
    type=str,
    default="WARNING",
    envvar="WEBHOOK_LOG_LEVEL",
    help="logging level",
)
@click.pass_context
def webhook(
    ctx,
    addr,
    port,
    debug,
    tunnel,
    relay_url,
    relay_key,
    relay_header,
    enable_buffer,
    moralis_api_key,
    log_level,
):
    """webhook endpoint server commands"""
    if debug:
        log_level = "DEBUG"
    logging.basicConfig(level=log_level)
    logger.setLevel(log_level)

    if ctx.obj is None:
        ctx.obj = dict(ehandler=ExceptionHandler(debug))
    kwargs = {}
    kwargs["addr"] = addr
    kwargs["port"] = port
    kwargs["debug"] = debug
    kwargs["tunnel"] = tunnel
    kwargs["relay_url"] = relay_url
    kwargs["relay_key"] = relay_key
    kwargs["relay_header"] = relay_header
    kwargs["enable_buffer"] = enable_buffer
    kwargs["moralis_api_key"] = moralis_api_key
    ctx.obj.update(**kwargs)
    ctx.obj["webhook"] = Webhook(**kwargs)


@webhook.command
@click.pass_context
@click.option("-q", "--quiet", is_flag=True)
def ps(ctx, quiet):
    """test for running server"""
    webhook = ctx.obj["webhook"]
    procs = webhook.processes()
    if bool(procs):
        ret = 0
        if not quiet:
            for proc in procs:
                click.echo(repr(proc))
    else:
        ret = -1
    sys.exit(ret)


@webhook.command
@click.pass_context
def hello(ctx):
    """output the ngrok public url"""
    webhook = ctx.obj["webhook"]
    output(webhook.hello())


@webhook.command
@click.pass_context
def tunnel(ctx):
    """output the ngrok public url"""
    webhook = ctx.obj["webhook"]
    output(webhook.tunnel_url())


@webhook.command
@click.option(
    "-e",
    "--enable",
    "buffer_enabled",
    flag_value=True,
    default=None,
    help="enable event buffer",
)
@click.option(
    "-d",
    "--disable",
    "buffer_enabled",
    flag_value=False,
    default=None,
    help="disable event buffer",
)
@click.pass_context
def buffer(ctx, buffer_enabled):
    """enable or disable the event buffer"""
    if buffer_enabled is None:
        kwargs = {}
    else:
        kwargs = dict(enable=buffer_enabled)
    webhook = ctx.obj["webhook"]
    output(webhook.buffer(**kwargs))


@webhook.command
@click.option(
    "-e",
    "--enable",
    "relay_enabled",
    flag_value=True,
    default=None,
    help="enable event relay",
)
@click.option(
    "-d",
    "--disable",
    "relay_enabled",
    flag_value=False,
    default=None,
    help="disable event relay",
)
@click.pass_context
def relay(ctx, relay_enabled):
    """set the configuration"""
    webhook = ctx.obj["webhook"]
    output(
        webhook.relay(
            url=ctx.obj["relay_url"],
            header=ctx.obj["relay_header"],
            key=ctx.obj["relay_key"],
            enable=relay_enabled,
        )
    )


@webhook.command
@click.option("-m", "--message", type=str, help="create json message data")
@click.argument("input", default="-", type=click.File("r"))
@click.pass_context
def inject(ctx, message, input):
    """inject an event"""
    webhook = ctx.obj["webhook"]
    if message:
        data = dict(message=message)
    else:
        data = json.load(input)
    output(webhook.inject(data))


@webhook.command
@click.argument("event-id", type=str)
@click.pass_context
def event(ctx, event_id):
    """get an event by id"""
    webhook = ctx.obj["webhook"]
    output(webhook.event(event_id))


@webhook.command
@click.argument("event-id", type=str)
@click.pass_context
def delete(ctx, event_id):
    """delete an event by id"""
    webhook = ctx.obj["webhook"]
    output(webhook.delete(event_id))


@webhook.command
@click.pass_context
def clear(ctx):
    """clear the webhook sever event buffer"""
    webhook = ctx.obj["webhook"]
    output(webhook.clear())


@webhook.command
@click.argument("output", default="-", type=click.File("w"))
@click.pass_context
def events(ctx, output):
    """output events received by the webhook server"""
    webhook = ctx.obj["webhook"]
    json.dump(webhook.events(), output, indent=2)
    output.write("\n")


@webhook.command
@click.option(
    "-l",
    "--logfile",
    envvar="TUNNEL_LOGFILE",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
)
@click.option(
    "-w/-W",
    "--wait/--no-wait",
    is_flag=True,
    default=True,
    help="wait for server startup",
)
@click.pass_context
def start(ctx, logfile, wait):
    """start local webhook server process with optional ngrok tunnel"""
    kwargs = ctx.obj.copy()
    webhook = kwargs.pop("webhook")
    kwargs.pop("ehandler")
    kwargs["logfile"] = logfile
    kwargs["wait"] = wait

    if webhook.server_running():
        fail("already running")
    else:
        click.echo("starting webhook server...", nl=False, err=True)
        proc = webhook.start(logfile, wait)
        if wait:
            while not webhook.server_running():
                if proc.poll() is not None:
                    click.echo("error")
                    fail(f"process {proc.args} returned {proc.returncode}")
                click.echo(".", nl=False, err=True)

        click.echo("started", err=True)


@webhook.command
@click.option(
    "-w/-W",
    "--wait/--no-wait",
    is_flag=True,
    default=True,
    help="wait for server shutdown",
)
@click.pass_context
def stop(ctx, wait):
    """stop the webhook server"""
    webhook = ctx.obj["webhook"]
    if not webhook.server_running():
        fail("not running")
    else:
        click.echo(webhook.shutdown(), err=True, nl=False)
    while webhook.server_running():
        click.echo(".", err=True, nl=False)
    click.echo("stopped", err=True)


@webhook.command
@click.option(
    "--ngrok-token",
    type=str,
    envvar="NGROK_AUTHTOKEN",
    show_envvar=True,
    help="ngrok auth token",
)
@click.option(
    "-w",
    "--workers",
    type=int,
    default=1,
    help="number of worker threads/processes",
)
@click.pass_context
def server(ctx, ngrok_token, workers):
    """run webhook server process"""
    from .server import ServerProcess

    config = ctx.obj.copy()
    config.pop("ehandler")
    config["ngrok_token"] = ngrok_token
    config["workers"] = workers
    ServerProcess(**config).run()
