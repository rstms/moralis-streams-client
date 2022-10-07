# moralis streams client CLI

import json
import logging
import sys

import click

from .api import REGIONS, STREAM_STATUS, MoralisStreamsApi
from .defaults import MORALIS_STREAMS_URL, SERVER_ADDR, SERVER_PORT
from .exception_handler import ExceptionHandler
from .version import __timestamp__, __version__

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
    envvar="MORALIS_API_KEY",
    show_envvar=True,
    default=None,
    help="API Key",
)
@click.option("-v", "--verbose", is_flag=True, help="output more detail")
@click.pass_context
def cli(ctx, debug, url, key, verbose):
    """Moralis Streams API CLI"""
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug
    ctx.obj["api"] = MoralisStreamsApi(key, url)


@cli.command()
@click.option(
    "-h",
    "--addr",
    type=str,
    envvar="MSC_WEBHOOK_ADDR",
    default=SERVER_ADDR,
    help="IP addr",
)
@click.option(
    "-p",
    "--port",
    type=int,
    envvar="MSC_WEBHOOK_PORT",
    default=SERVER_PORT,
    help="listen port",
)
@click.option(
    "-w",
    "--workers",
    type=int,
    default=1,
    help="number of worker threads/processes",
)
@click.option("-n", "--ngrok", is_flag=True, help="enable ngrok tunnel")
@click.option(
    "--ngrok-auth-token",
    type=str,
    envvar="NGROK_AUTH_TOKEN",
    show_envvar=True,
    help="ngrok auth token",
)
@click.pass_context
def webhook_server(ctx, addr, port, workers, ngrok, ngrok_auth_token):
    """webhook endpoint server"""

    from .server import run

    if ctx.obj["debug"]:
        level = "debug"
    else:
        level = "info"

    sys.exit(
        run(addr, port, workers, level, tunnel=ngrok, token=ngrok_auth_token)
    )


def class_strings(_class):
    class_dict = _class.__dict__
    return [
        name
        for name, member in class_dict.items()
        if isinstance(member, str) and not name.startswith("__")
    ]


class Response:
    pass


def output(result):
    if isinstance(result, Response):
        result = dict(
            status_code=result.status_code,
            headers=dict(result.headers),
            content=f"{result.content}",
            parsed=result.parsed,
        )
    elif result is None:
        result = {}
    elif isinstance(result, dict):
        pass
    elif hasattr(result, "to_dict"):
        result = result.to_dict()
    else:
        raise TypeError(f"unexpected result type {type(result)}: {result}")
    click.echo(json.dumps(result, indent=2))


@cli.command
@click.pass_context
def get_stats(ctx):
    """output beta statistics"""
    output(ctx.obj["api"].get_stats())


@cli.command
@click.option(
    "-l",
    "--limit",
    type=int,
    default=100,
    help="number of items in each result",
)
@click.option(
    "-c", "--cursor", type=str, help="cursor for the next set of items"
)
@click.option(
    "-x", "--exclude-payload", is_flag=True, help="exclude payload in response"
)
@click.pass_context
def get_history(ctx, limit, cursor, exclude_payload):
    """output event history"""
    output(ctx.obj["api"].get_history(limit, cursor, exclude_payload))


@cli.command
@click.argument("event-id", type=str)
@click.pass_context
def replay_history(ctx, event_id):
    """request resend of event callback"""
    output(ctx.obj["api"].replay_history(event_id))


@cli.command
@click.pass_context
def get_settings(ctx):
    """get settings"""
    output(ctx.obj["api"].get_settings())


@cli.command
@click.pass_context
@click.argument("region", type=click.Choice(REGIONS))
def set_settings(ctx, region):
    """set settings"""
    output(ctx.obj["api"].set_settings(region))


@cli.command
@click.option(
    "-c",
    "--chain-id",
    type=str,
    multiple=True,
    help='The ids of the chains for this stream in hex Ex: ["0x1","0x38"]',
)
@click.option(
    "-t",
    "--topic",
    multiple=True,
    help="The topic0 of the event in hex (required for CONTRACT",
)
@click.option(
    "-A",
    "--all-addresses",
    is_flag=True,
    help="Include events for all addresses (only applied when abi and topic0 is provided)",
)
@click.option(
    "-n",
    "--include-native-txs",
    is_flag=True,
    help="Include native transactions defaults to false (contract only)",
)
@click.option(
    "-l",
    "--include-contract-logs",
    is_flag=True,
    help="Include events for all addresses (only applied when abi and topic0 is provided)",
)
@click.option(
    "-i",
    "--include-internal-txs",
    is_flag=True,
    help="Include events for all addresses (only applied when abi and topic0 is provided)",
)
@click.option(
    "-a",
    "--abi",
    type=str,
    multiple=True,
    help="The abi to parse the log object of the contract",
)
@click.option(
    "-o",
    "--option",
    multiple=True,
    type=str,
    help="json string of Advanced Options {topic0: str, filter: str, include_native_txs: bool}",
)
@click.argument("webhook_url", type=str)
@click.argument("description", type=str)
@click.argument("tag", type=str)
@click.pass_context
def create_stream(
    ctx,
    topic,
    all_addresses,
    include_native_txs,
    include_contract_logs,
    include_internal_txs,
    abi,
    option,
    chain_id,
    webhook_url,
    description,
    tag,
):
    """create new stream"""

    api = ctx.obj["api"]
    ret = api.create_stream(
        webhook_url=webhook_url,
        description=description,
        tag=tag,
        topic0=list(topic),
        all_addresses=all_addresses,
        include_native_txs=include_native_txs,
        include_contract_logs=include_contract_logs,
        include_internal_txs=include_internal_txs,
        abi=list(abi),
        advanced_options=list(option),
        chain_ids=list(chain_id),
    )
    output(ret)


@cli.command
@click.argument("stream-id", type=str)
@click.option(
    "-a",
    "--address",
    multiple=True,
    type=str,
    help="address to add (multiples ok)",
)
@click.pass_context
def add_address_to_stream(ctx, stream_id, address):
    """delete stream identified by stream-id"""
    api = ctx.obj["api"]
    ret = api.add_address_to_stream(stream_id, list(address))
    output(ret)


@cli.command
@click.argument("stream-id", type=str)
@click.option("-a", "--address", type=str, help="address to remove")
@click.pass_context
def delete_address_from_stream(ctx, stream_id, address):
    """delete an address from the stream identified by stream-id"""
    api = ctx.obj["api"]
    ret = api.delete_addresses_from_stream(stream_id, address)
    output(ret)


@cli.command
@click.argument("stream-id", type=str)
@click.pass_context
def delete_stream(ctx, stream_id):
    """delete stream identified by stream-id"""
    api = ctx.obj["api"]
    ret = api.delete_stream(stream_id)
    output(ret)


@cli.command
@click.argument("stream-id", type=str)
@click.option(
    "-l",
    "--limit",
    type=int,
    default=100,
    help="number of items in each result",
)
@click.option(
    "-c", "--cursor", type=str, help="cursor for the next set of items"
)
@click.pass_context
def get_addresses(ctx, stream_id, limit, cursor):
    """list addresses associated with the stream identified by stream-id"""
    api = ctx.obj["api"]
    ret = api.delete_stream(stream_id, limit=limit, cursor=cursor)
    output(ret)


@cli.command
@click.option(
    "-i", "--stream-id", type=str, help="stream_id, default is all streams"
)
@click.option(
    "-l",
    "--limit",
    type=int,
    default=100,
    help="number of items in each result",
)
@click.option(
    "-c", "--cursor", type=str, help="cursor for the next set of items"
)
@click.pass_context
def get_streams(ctx, stream_id, limit, cursor):
    """list one or all streams"""
    api = ctx.obj["api"]
    if stream_id is None:
        ret = api.get_streams(limit=limit, cursor=cursor)
    else:
        ret = api.get_stream(stream_id)
    output(ret)


@cli.command
@click.option(
    "-c",
    "--chain-id",
    type=str,
    multiple=True,
    help='The ids of the chains for this stream in hex Ex: ["0x1","0x38"]',
)
@click.option(
    "-t",
    "--topic",
    multiple=True,
    help="The topic0 of the event in hex (required for CONTRACT",
)
@click.option(
    "-A",
    "--all-addresses",
    is_flag=True,
    help="Include events for all addresses (only applied when abi and topic0 is provided)",
)
@click.option(
    "-n",
    "--include-native-txs",
    is_flag=True,
    help="Include native transactions defaults to false (contract only)",
)
@click.option(
    "-l",
    "--include-contract-logs",
    is_flag=True,
    help="Include events for all addresses (only applied when abi and topic0 is provided)",
)
@click.option(
    "-i",
    "--include-internal-txs",
    is_flag=True,
    help="Include events for all addresses (only applied when abi and topic0 is provided)",
)
@click.option(
    "-a",
    "--abi",
    type=str,
    multiple=True,
    help="The abi to parse the log object of the contract",
)
@click.option(
    "-o",
    "--option",
    multiple=True,
    type=str,
    help="json string of Advanced Options {topic0: str, filter: str, include_native_txs: bool}",
)
@click.argument("stream-id", type=str)
@click.argument("webhook-url", type=str)
@click.argument("description", type=str)
@click.argument("tag", type=str)
@click.pass_context
def update_stream(
    ctx,
    stream_id,
    webhook_url,
    description,
    tag,
    topic,
    all_addresses,
    include_native_txs,
    include_contract_logs,
    include_internal_txs,
    abi,
    option,
    chain_id,
):
    """update stream parameters"""
    api = ctx.obj["api"]

    ret = api.update_stream(
        id=stream_id,
        webhook_url=webhook_url,
        description=description,
        tag=tag,
        topic0=list(topic),
        all_addresses=all_addresses,
        include_native_txs=include_native_txs,
        include_contract_logs=include_contract_logs,
        include_internal_txs=include_internal_txs,
        abi=list(abi),
        advanced_options=list(option),
        chain_ids=list(chain_id),
    )
    output(ret)


@cli.command
@click.argument("stream-id", type=str)
@click.argument("status", type=click.Choice(STREAM_STATUS))
@click.pass_context
def update_stream_status(ctx, stream_id, status):
    """update the status of a stream to active, paused, or error"""
    api = ctx.obj["api"]
    ret = api.update_stream_status(stream_id, status)
    output(ret)


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
