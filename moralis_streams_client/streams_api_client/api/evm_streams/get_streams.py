from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...models.streams_types_streams_response import (
    StreamsTypesStreamsResponse,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    limit: float,
    cursor: Union[Unset, None, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/streams/evm".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["limit"] = limit

    params["cursor"] = cursor

    params = {
        k: v for k, v in params.items() if v is not UNSET and v is not None
    }

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[StreamsTypesStreamsResponse]:
    if response.status_code == 200:
        response_200 = StreamsTypesStreamsResponse.from_dict(response.json())

        return response_200
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[StreamsTypesStreamsResponse]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    limit: float,
    cursor: Union[Unset, None, str] = UNSET,
) -> Response[StreamsTypesStreamsResponse]:
    """Get all the evm streams for the current project based on the project api-key.

    Args:
        limit (float):
        cursor (Union[Unset, None, str]):

    Returns:
        Response[StreamsTypesStreamsResponse]
    """

    kwargs = _get_kwargs(
        client=client,
        limit=limit,
        cursor=cursor,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    limit: float,
    cursor: Union[Unset, None, str] = UNSET,
) -> Optional[StreamsTypesStreamsResponse]:
    """Get all the evm streams for the current project based on the project api-key.

    Args:
        limit (float):
        cursor (Union[Unset, None, str]):

    Returns:
        Response[StreamsTypesStreamsResponse]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        cursor=cursor,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    limit: float,
    cursor: Union[Unset, None, str] = UNSET,
) -> Response[StreamsTypesStreamsResponse]:
    """Get all the evm streams for the current project based on the project api-key.

    Args:
        limit (float):
        cursor (Union[Unset, None, str]):

    Returns:
        Response[StreamsTypesStreamsResponse]
    """

    kwargs = _get_kwargs(
        client=client,
        limit=limit,
        cursor=cursor,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    limit: float,
    cursor: Union[Unset, None, str] = UNSET,
) -> Optional[StreamsTypesStreamsResponse]:
    """Get all the evm streams for the current project based on the project api-key.

    Args:
        limit (float):
        cursor (Union[Unset, None, str]):

    Returns:
        Response[StreamsTypesStreamsResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            cursor=cursor,
        )
    ).parsed
