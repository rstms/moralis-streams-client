# webhook server process

import json
import logging
import os
import sys
from multiprocessing import Process
from pathlib import Path
from subprocess import CalledProcessError, check_output

import asyncclick as click
from eth_hash.auto import keccak
from eth_utils import to_hex

from . import settings
from .exception_handler import ExceptionHandler
from .signature import Signature
from .webhook import Webhook


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
    "-d/-D",
    "--debug/--no-debug",
    default=None,
    is_flag=True,
    help="output full stacktrace on exceptions",
)
@click.option(
    "-a",
    "--addr",
    type=str,
    help="server listen IP addr",
)
@click.option(
    "-p",
    "--port",
    type=int,
    help="server listen port",
)
@click.option(
    "-t/-T",
    "--tunnel/--no-tunnel",
    is_flag=True,
    default=None,
    help="enable/disable ngrok tunnel",
)
@click.option(
    "-r",
    "--relay-url",
    type=str,
    help="enable relay to URL",
)
@click.option(
    "-k",
    "--relay-key",
    type=str,
    help="relay API key",
)
@click.option(
    "-h",
    "--relay-header",
    type=str,
    help="header name for relay API key",
)
@click.option(
    "-b/-B",
    "--enable-buffer/--disable-buffer",
    is_flag=True,
    default=None,
    help="enable/disable event buffer",
)
@click.option(
    "-m",
    "--moralis-api-key",
    type=str,
    help="Moralis Streams API key",
)
@click.option(
    "-l",
    "--log-level",
    type=str,
    help="logging level",
)
@click.option(
    "-f",
    "--log-file",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    help="log to file",
)
@click.pass_context
def webhook(
    ctx,
    debug,
    addr,
    port,
    tunnel,
    relay_url,
    relay_key,
    relay_header,
    enable_buffer,
    moralis_api_key,
    log_level,
    log_file,
):
    """webhook endpoint server commands"""

    # webhook cli options may override settings
    if debug is not None:
        settings.DEBUG = debug
    if addr:
        settings.ADDR = addr
    if port:
        settings.PORT = port
    if tunnel is not None:
        settings.TUNNEL = tunnel
    if relay_url:
        settings.RELAY_URL = relay_url
    if relay_key:
        settings.RELAY_KEY = relay_key
    if relay_header:
        settings.RELAY_HEADER = relay_header
    if enable_buffer is not None:
        settings.BUFFER_ENABLE = enable_buffer
    if moralis_api_key:
        settings.MORALIS_API_KEY = moralis_api_key
    if log_level:
        settings.LOG_LEVEL = log_level
    if log_file:
        settings.LOG_FILE = str(log_file.resolve())

    if ctx.obj is None:
        ctx.obj = dict(ehandler=ExceptionHandler(debug))

    ctx.obj["webhook"] = Webhook()


@webhook.command
@click.pass_context
@click.option("-q", "--quiet", is_flag=True)
async def ps(ctx, quiet):
    """test for running server"""
    webhook = ctx.obj["webhook"]
    procs = await webhook.processes()
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
async def hello(ctx):
    """output the ngrok public url"""
    webhook = ctx.obj["webhook"]
    output(await webhook.hello())


@webhook.command
@click.pass_context
async def tunnel(ctx):
    """output the ngrok public url"""
    webhook = ctx.obj["webhook"]
    output(await webhook.tunnel_url())


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
async def buffer(ctx, buffer_enabled):
    """enable or disable the event buffer"""
    if buffer_enabled is None:
        kwargs = {}
    else:
        kwargs = dict(enable=buffer_enabled)
    webhook = ctx.obj["webhook"]
    output(await webhook.buffer(**kwargs))


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
async def relay(ctx, relay_enabled):
    """set the configuration"""
    webhook = ctx.obj["webhook"]
    output(
        await webhook.relay(
            url=settings.RELAY_URL,
            header=settings.RELAY_HEADER,
            key=str(settings.RELAY_KEY),
            enable=relay_enabled,
        )
    )


@webhook.command
@click.option("-m", "--message", type=str, help="create json message data")
@click.argument("input", default="-", type=click.File("r"))
@click.pass_context
async def inject(ctx, message, input):
    """inject an event"""
    webhook = ctx.obj["webhook"]
    if message:
        data = dict(message=message)
    else:
        data = json.load(input)
    output(await webhook.inject(data))


@webhook.command
@click.argument("event-id", type=str)
@click.pass_context
async def event(ctx, event_id):
    """get an event by id"""
    webhook = ctx.obj["webhook"]
    output(await webhook.event(event_id))


@webhook.command
@click.argument("event-id", type=str)
@click.pass_context
async def delete(ctx, event_id):
    """delete an event by id"""
    webhook = ctx.obj["webhook"]
    output(await webhook.delete(event_id))


@webhook.command
@click.pass_context
async def clear(ctx):
    """clear the webhook sever event buffer"""
    webhook = ctx.obj["webhook"]
    output(await webhook.clear())


@webhook.command
@click.argument("output", default="-", type=click.File("w"))
@click.pass_context
async def events(ctx, output):
    """output events received by the webhook server"""
    webhook = ctx.obj["webhook"]
    json.dump(await webhook.events(), output, indent=2)
    output.write("\n")


@webhook.command
@click.option(
    "-w/-W",
    "--wait/--no-wait",
    is_flag=True,
    default=True,
    help="wait for server startup",
)
@click.pass_context
async def start(ctx, wait):
    """start local webhook server process with optional ngrok tunnel"""
    kwargs = ctx.obj.copy()
    webhook = kwargs.pop("webhook")
    kwargs.pop("ehandler")

    if await webhook.server_running():
        fail("already running")
    else:
        click.echo("starting webhook server...", nl=False, err=True)
        proc = await webhook.start(wait)
        if wait:
            while not await webhook.server_running():
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
async def stop(ctx, wait):
    """stop the webhook server"""
    webhook = ctx.obj["webhook"]
    if not await webhook.server_running():
        fail("not running")
    else:
        click.echo(await webhook.shutdown(), err=True, nl=False)
    while await webhook.server_running():
        click.echo(".", err=True, nl=False)
    click.echo("stopped", err=True)
