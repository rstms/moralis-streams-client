from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...models.streams_types_streams_model import StreamsTypesStreamsModel
from ...models.streams_types_streams_model_create import (
    StreamsTypesStreamsModelCreate,
)
from ...types import UNSET, Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    json_body: StreamsTypesStreamsModelCreate,
) -> Dict[str, Any]:
    url = "{}/streams/evm".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body.to_dict()

    return {
        "method": "put",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[StreamsTypesStreamsModel]:
    if response.status_code == 200:
        response_200 = StreamsTypesStreamsModel.from_dict(response.json())

        return response_200
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[StreamsTypesStreamsModel]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    json_body: StreamsTypesStreamsModelCreate,
) -> Response[StreamsTypesStreamsModel]:
    """Creates a new evm stream.

    Args:
        json_body (StreamsTypesStreamsModelCreate):

    Returns:
        Response[StreamsTypesStreamsModel]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    json_body: StreamsTypesStreamsModelCreate,
) -> Optional[StreamsTypesStreamsModel]:
    """Creates a new evm stream.

    Args:
        json_body (StreamsTypesStreamsModelCreate):

    Returns:
        Response[StreamsTypesStreamsModel]
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    json_body: StreamsTypesStreamsModelCreate,
) -> Response[StreamsTypesStreamsModel]:
    """Creates a new evm stream.

    Args:
        json_body (StreamsTypesStreamsModelCreate):

    Returns:
        Response[StreamsTypesStreamsModel]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    json_body: StreamsTypesStreamsModelCreate,
) -> Optional[StreamsTypesStreamsModel]:
    """Creates a new evm stream.

    Args:
        json_body (StreamsTypesStreamsModelCreate):

    Returns:
        Response[StreamsTypesStreamsModel]
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
