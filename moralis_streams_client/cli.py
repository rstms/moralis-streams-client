"""Console script for moralis_streams_client."""

import sys

import click

from .exception_handler import ExceptionHandler
from .version import __timestamp__, __version__

MORALIS_STREAMS_URL = "https://api.moralis-streams.com"

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


@click.group(name="msc")
@click.version_option(message=header)
@click.option("-d", "--debug", is_flag=True, help="debug mode")
@click.option(
    "-u",
    "--url",
    type=str,
    envvar="MORALIS_STREAMS_URL",
    show_envvar=True,
    default=MORALIS_STREAMS_URL,
    help="moralis streams API base URL",
)
@click.option(
    "-k",
    "--key",
    type=str,
    required=True,
    envvar="MORALIS_API_KEY",
    show_envvar=True,
    default=None,
    help="API Key",
)
@click.pass_context
def msc(ctx, debug, url, key):
    """Moralis Streams API CLI"""
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug
    ctx.obj["url"] = url
    ctx.obj["key"] = key
    ctx.obj["api"] = None


@msc.command
@click.pass_context
def settings(ctx):
    """get or set settings"""


@msc.command
@click.argument("tag", type=str)
@click.pass_context
def mkstr(ctx, tag):
    """create new EVM stream"""
    pass


@msc.command
@click.argument("tag", type=str)
@click.pass_context
def rmstr(ctx, tag):
    """delete EVM stream identified by TAG"""
    pass


@msc.command
@click.pass_context
def ls(ctx):
    """list EVM streams"""
    pass


if __name__ == "__main__":
    sys.exit(msc())  # pragma: no cover
