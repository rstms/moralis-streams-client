"""Console script for moralis_streams_client."""

import json
import sys

import click

from .api import (
    AddressesTypesAddressesAdd,
    AddressesTypesAddressesRemove,
    PartialStreamsTypesStreamsModelCreate,
    Response,
    SettingsRegion,
    SettingsTypesSettingsModel,
    StreamsStatus,
    StreamsType,
    StreamsTypesStreamsModelCreate,
    StreamsTypesStreamsStatusUpdate,
    connect,
)
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
@click.option("-v", "--verbose", is_flag=True, help="output more detail")
@click.pass_context
def cli(ctx, debug, url, key, verbose):
    """Moralis Streams API CLI"""
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["api"] = connect(url=url, key=key, detailed=verbose)
    ctx.obj["debug"] = debug


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
def stats(ctx):
    """output beta statistics"""
    api = ctx.obj["api"]
    output(api.get_stats())


@cli.command
@click.pass_context
def get_settings(ctx):
    """get settings"""
    output(ctx.obj["api"].get_settings())


@cli.command
@click.pass_context
@click.argument(
    "region",
    type=click.option(
        [name for name, member in SettingsRegion.__members__.items()]
    ),
)
def set_settings(ctx, region):
    """set settings"""
    settings = SettingsTypesSettingsModel.from_dict({"region": region})
    output(ctx.obj["api"].set_settings(settings))


@cli.command
@click.option(
    "-i",
    "--chain-id",
    type=str,
    multiple=True,
    help='The ids of the chains for this stream in hex Ex: ["0x1","0x38"]',
)
@click.option(
    "-t",
    "--stream-type",
    type=click.Choice(
        [name for name, member in StreamsType.__members__.items()]
    ),
)
@click.option(
    "-T",
    "--topic",
    help="The topic0 of the event in hex (required for CONTRACT",
)
@click.option(
    "-n",
    "--include-native",
    is_flag=True,
    help="Include native transactions defaults to false (contract only)",
)
@click.option(
    "-a",
    "--abi",
    type=str,
    help="The abi to parse the log object of the contract",
)
@click.option(
    "-f",
    "--filter",
    "filter_",
    type=str,
    help="The filter object, optional (contract only)",
)
@click.argument("tag", type=str)
@click.argument("url", type=str)
@click.argument("description", type=str)
@click.argument("address", type=str)
@click.pass_context
def create_stream(
    ctx,
    url,
    description,
    tag,
    chain_id,
    stream_type,
    topic,
    include_native,
    abi,
    filter_,
    address,
):
    """create new stream
    URL: Webhook URL where moralis will send the POST request.
    TAG: an identifier for this stream
    ADDRESS: The wallet address of the user or the contract address

    WALLET: listens to all native transactions of the address and all
    logs where the address is involved in at least one of the topics

    CONTRACT: listens to all native transactions of the address and
    all logs produced by the contract address
    """
    api = ctx.obj["api"]
    if stream_type == "contract":
        ret = api.create_stream(
            json_body=StreamsTypesStreamsModelCreate(
                webhook_url=url,
                description=description,
                tag=tag,
                chain_ids=list(chain_id),
                type="contract",
                token_address=address,
                topic0=topic,
                include_native_txs=include_native,
                abi=abi,
                filter_=filter_,
            )
        )
    elif stream_type == "wallet":
        ret = api.create_stream(
            json_body=StreamsTypesStreamsModelCreate(
                webhook_url=url,
                description=description,
                tag=tag,
                chain_ids=list(chain_id),
                type="wallet",
                address=address,
            )
        )
    else:
        raise ValueError(f"unrecognized stream type: {stream_type}")
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
    ret = api.add_address_to_stream(
        stream_id, json_body=AddressesTypesAddressesAdd(address=list(address))
    )
    output(ret)


@cli.command
@click.argument("stream-id", type=str)
@click.option("-a", "--address", type=str, help="address to remove")
@click.pass_context
def delete_address_from_stream(ctx, stream_id, address):
    """delete an address from the stream identified by stream-id"""
    api = ctx.obj["api"]
    ret = api.delete_addresses_from_stream(
        stream_id, json_body=AddressesTypesAddressesRemove(address=address)
    )
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
    "-l", "--limit", type=float, help="number of items in each result"
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
    "-l", "--limit", type=float, help="number of items in each result"
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
    "-i",
    "--chain-id",
    type=str,
    multiple=True,
    help='The ids of the chains for this stream in hex Ex: ["0x1","0x38"]',
)
@click.option(
    "-t",
    "--stream-type",
    type=click.Choice(
        [name for name, member in StreamsType.__members__.items()]
    ),
)
@click.option(
    "-T",
    "--topic",
    help="The topic0 of the event in hex (required for CONTRACT",
)
@click.option(
    "-n",
    "--include-native",
    is_flag=True,
    help="Include native transactions defaults to false (contract only)",
)
@click.option(
    "-a",
    "--abi",
    type=str,
    help="The abi to parse the log object of the contract",
)
@click.option(
    "-f",
    "--filter",
    "filter_",
    type=str,
    help="The filter object, optional (contract only)",
)
@click.argument("stream-id", type=str)
@click.argument("tag", type=str)
@click.argument("url", type=str)
@click.argument("description", type=str)
@click.argument("address", type=str)
@click.pass_context
def update_stream(
    ctx,
    stream_id,
    url,
    description,
    tag,
    chain_id,
    stream_type,
    topic,
    include_native,
    abi,
    filter_,
    address,
):
    """update stream parameters"""
    api = ctx.obj["api"]

    if stream_type == "contract":
        ret = api.update_stream(
            id=stream_id,
            json_body=PartialStreamsTypesStreamsModelCreate(
                webhook_url=url,
                description=description,
                tag=tag,
                chain_ids=list(chain_id),
                type="contract",
                token_address=address,
                topic0=topic,
                include_native_txs=include_native,
                abi=abi,
                filter_=filter_,
            ),
        )
    elif stream_type == "wallet":
        ret = api.update_stream(
            id=stream_id,
            json_body=PartialStreamsTypesStreamsModelCreate(
                webhook_url=url,
                description=description,
                tag=tag,
                chain_ids=list(chain_id),
                type="wallet",
                address=address,
            ),
        )
    output(ret)


@cli.command
@click.argument("stream-id", type=str)
@click.argument(
    "status",
    type=click.Choice(
        [name for name, member in StreamsStatus.__members__.items()]
    ),
)
@click.pass_context
def update_stream_status(ctx, stream_id, status):
    """update the status of a stream to active, paused, or error"""
    api = ctx.obj["api"]
    ret = api.update_stream_status(
        stream_id, json_body=StreamsTypesStreamsStatusUpdate(status=status)
    )
    output(ret)


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
