# webhook server process

import json
import logging
import os
import sys
from pathlib import Path
from subprocess import DEVNULL, STDOUT, CalledProcessError, Popen, check_output

import click
import requests
from eth_hash.auto import keccak
from eth_utils import to_hex

from .auth import Signature
from .defaults import SERVER_ADDR, SERVER_PORT

logger = logging.getLogger(__name__)
debug = logger.debug


def output(data):
    click.echo(json.dumps(data, indent=2))


def fail(error):
    click.echo(f"Error: {error}", err=True)
    sys.exit(-1)


def run(cmd):
    return check_output(cmd, shell=True).decode()


def _url(ctx, path):
    if ctx.obj.pop("tunnel", None):
        return f"{get(ctx, 'tunnel')['tunnel_url']}/{path}"
    else:
        return f"http://{ctx.obj['addr']}:{ctx.obj['port']}/{path}"


def get(ctx, path):
    try:
        result = requests.get(_url(ctx, path))
        result.raise_for_status()
    except Exception as ex:
        fail(ex)
    return result.json()["result"]


def post(ctx, path, data={}, headers={}):
    headers = ctx.obj["auth"].headers(data)
    try:
        result = requests.post(_url(ctx, path), json=data, headers=headers)
        result.raise_for_status()
    except Exception as ex:
        fail(ex)

    return result.json()["result"]


@click.group
@click.option(
    "-a",
    "--addr",
    type=str,
    envvar="WEBHOOK_SERVER_ADDR",
    default=SERVER_ADDR,
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
    default=SERVER_PORT,
    show_envvar=True,
    help="server listen port",
)
@click.option(
    "-t/-T",
    "--tunnel/--no-tunnel",
    is_flag=True,
    default=True,
    help="enable/disable ngrok tunnel",
)
@click.option("-d", "--debug", is_flag=True)
@click.pass_context
def webhook(ctx, addr, port, tunnel, debug):
    """webhook endpoint server commands"""
    if isinstance(ctx.obj, dict) is False:
        ctx.obj = {}
        ctx.obj["debug"] = debug
    ctx.obj["auth"] = Signature()
    ctx.obj["addr"] = addr
    ctx.obj["port"] = port
    ctx.obj["tunnel"] = tunnel


@webhook.command
@click.option("-q", "--quiet", is_flag=True)
@click.pass_context
def ps(ctx, quiet):
    """test for running server"""
    if server_running(quiet):
        ret = 0
    else:
        ret = 1
    sys.exit(ret)


PATTERN = "'[m]sc.*webhook.*server$'"


def server_running(quiet=True):
    try:
        run(f"pgrep -f {PATTERN}")
    except CalledProcessError:
        return False
    if not quiet:
        lines = run(f"pgrep -af {PATTERN}").strip().split("\n")
        output(lines)
    return True


@webhook.command
@click.pass_context
def url(ctx):
    """output the ngrok public url"""
    output(get(ctx, "tunnel")["tunnel_url"])


@webhook.command
@click.pass_context
def hello(ctx):
    """send and recieve a friendly greeting"""
    output(get(ctx, "hello"))


@webhook.command
@click.pass_context
def clear(ctx):
    """clear the webhook sever event buffer"""
    output(get(ctx, "clear"))


@webhook.command
@click.argument("output", default="-", type=click.File("w"))
@click.pass_context
def events(ctx, output):
    """output events received by the webhook server"""
    json.dump(get(ctx, "events"), output, indent=2)
    output.write("\n")


@webhook.command
@click.option(
    "-e",
    "--endpoint",
    type=str,
    envvar="TUNNEL_ENDPOINT",
    show_envvar=True,
    default="contract/event",
)
@click.argument("input", default="-", type=click.File("r"))
@click.pass_context
def call(ctx, endpoint, input):
    """read json from file or stdin and POST it to the webhook endpoint"""
    ctx.obj["tunnel"] = True
    data = json.load(input)
    output(post(ctx, endpoint, data=data))


@webhook.command
@click.option(
    "-l",
    "--logfile",
    envvar="TUNNEL_LOGFILE",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
)
@click.option(
    "-w/-W",
    "--wait-start/--no-wait-start",
    is_flag=True,
    default=True,
    help="wait for server startup",
)
@click.pass_context
def start(ctx, logfile, wait_start):
    """start local webhook server process with optional ngrok tunnel"""
    if server_running():
        fail("already running")
    else:
        click.echo("starting webhook server...", nl=False, err=True)
        if logfile is None:
            logfile = DEVNULL
        else:
            logfile = Path(logfile).open("a") or DEVNULL
        cmd = ["msc"]
        if ctx.obj["debug"]:
            cmd.append("--debug")
        cmd.extend(
            [
                "webhook",
                "--addr",
                ctx.obj["addr"],
                "--port",
                str(ctx.obj["port"]),
            ]
        )
        if ctx.obj["tunnel"]:
            cmd.append("--tunnel")
        cmd.append("server")

        debug(f"command: {cmd}")

        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        try:
            proc = Popen(
                cmd,
                env=env,
                stderr=STDOUT,
                stdout=logfile,
                bufsize=1,
            )
        except Exception as ex:
            fail(ex)

        if wait_start:
            while not server_running():
                if proc.poll() is not None:
                    click.echo("error")
                    fail(f"process {proc.args} returned {proc.returncode}")
                click.echo(".", nl=False, err=True)

        click.echo("started", err=True)


@webhook.command
@click.pass_context
def stop(ctx):
    """stop the webhook server"""
    if not server_running():
        fail("not running")
    else:
        click.echo(get(ctx, "shutdown"), err=True, nl=False)
    while server_running():
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

    ctx.obj["ngrok_token"] = ngrok_token
    ctx.obj["workers"] = workers
    ServerProcess(ctx.obj).run()
