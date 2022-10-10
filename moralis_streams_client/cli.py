# moralis streams client CLI

import json
import logging
import sys

import click

from .api import MoralisStreamsApi
from .defaults import REGION_CHOICES, STATUS_CHOICES, STREAMS_URL
from .exception_handler import ExceptionHandler
from .version import __timestamp__, __version__
from .webhook import webhook

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"

logger = logging.getLogger(__name__)
info = logger.info
debug = logger.debug


@click.group(name="msc")
@click.version_option(message=header)
@click.option("-d", "--debug", is_flag=True, help="debug mode")
@click.option(
    "-u",
    "--url",
    type=str,
    envvar="MORALIS_STREAMS_URL",
    show_envvar=True,
    default=STREAMS_URL,
    help="moralis streams API base URL",
)
@click.option(
    "-k",
    "--key",
    type=str,
    envvar="MORALIS_API_KEY",
    show_envvar=True,
    default=None,
    required=True,
    help="API Key",
)
@click.option(
    "-r",
    "--row-limit",
    type=int,
    default=100,
    envvar="MORALIS_STREAMS_API_ROW_LIMIT",
    show_envvar=True,
    show_default=True,
    help="number of items in each result page",
)
@click.option(
    "-p",
    "--page-limit",
    type=int,
    default=10000,
    envvar="MORALIS_STREAMS_API_PAGE_LIMIT",
    show_envvar=True,
    show_default=True,
    help="number of pages allowed in results",
)
@click.option("-v", "--verbose", is_flag=True, help="output more detail")
@click.pass_context
def cli(ctx, url, key, debug, verbose, row_limit, page_limit):
    """Moralis Streams API CLI"""
    if debug:
        level = logging.DEBUG
        if not verbose:
            logging.getLogger("urllib3.connectionpool").setLevel(
                logging.WARNING
            )

    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(
        level=level, handlers=[logging.StreamHandler(sys.stderr)]
    )

    info(header)

    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug
    ctx.obj["verbose"] = verbose
    ctx.obj["api"] = MoralisStreamsApi(
        api_key=key,
        url=url,
        debug=debug,
        row_limit=row_limit,
        page_limit=page_limit,
    )


def output(result):
    if result is None:
        result = {}
    elif isinstance(result, dict):
        pass
    elif isinstance(result, list):
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
    "-x/-X",
    "--exclude-payload/--no-exclude-payload",
    is_flag=True,
    help="exclude payload in response",
)
@click.pass_context
def get_history(ctx, exclude_payload):
    """output event history"""
    output(ctx.obj["api"].get_history(exclude_payload=exclude_payload))


@cli.command
@click.argument("event-id", type=str)
@click.pass_context
def replay_history(ctx, event_id):
    """request resend of history event"""
    output(ctx.obj["api"].replay_history(event_id))


@cli.command
@click.pass_context
def get_settings(ctx):
    """get settings"""
    output(ctx.obj["api"].get_settings())


@cli.command
@click.pass_context
@click.argument("region", type=click.Choice(REGION_CHOICES))
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
    "-a", "--abi", type=str, help="The contract abi as a JSON string"
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
        abi=json.loads(abi),
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
    """add one or more addresses to the stream identified by stream-id"""
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
@click.pass_context
def get_addresses(ctx, stream_id):
    """list addresses associated with the stream identified by stream-id"""
    api = ctx.obj["api"]
    ret = api.get_addresses(stream_id)
    output(ret)


@cli.command
@click.option(
    "-i", "--stream-id", type=str, help="stream_id, default is all streams"
)
@click.pass_context
def get_streams(ctx, stream_id):
    """list one or all streams"""
    api = ctx.obj["api"]
    if stream_id is None:
        ret = api.get_streams()
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
@click.argument("status", type=click.Choice(STATUS_CHOICES))
@click.pass_context
def update_stream_status(ctx, stream_id, status):
    """update the status of a stream to active, paused, or error"""
    api = ctx.obj["api"]
    ret = api.update_stream_status(stream_id, status)
    output(ret)


cli.add_command(webhook)


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
