from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...models.streams_types_streams_model import StreamsTypesStreamsModel
from ...types import UNSET, Response


def _get_kwargs(
    id: str,
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/streams/evm/{id}".format(client.base_url, id=id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
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
    id: str,
    *,
    client: AuthenticatedClient,
) -> Response[StreamsTypesStreamsModel]:
    """Get a specific evm stream.

    Args:
        id (str): Stringified UUIDv4.
            See [RFC 4112](https://tools.ietf.org/html/rfc4122)

    Returns:
        Response[StreamsTypesStreamsModel]
    """

    kwargs = _get_kwargs(
        id=id,
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[StreamsTypesStreamsModel]:
    """Get a specific evm stream.

    Args:
        id (str): Stringified UUIDv4.
            See [RFC 4112](https://tools.ietf.org/html/rfc4122)

    Returns:
        Response[StreamsTypesStreamsModel]
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
) -> Response[StreamsTypesStreamsModel]:
    """Get a specific evm stream.

    Args:
        id (str): Stringified UUIDv4.
            See [RFC 4112](https://tools.ietf.org/html/rfc4122)

    Returns:
        Response[StreamsTypesStreamsModel]
    """

    kwargs = _get_kwargs(
        id=id,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[StreamsTypesStreamsModel]:
    """Get a specific evm stream.

    Args:
        id (str): Stringified UUIDv4.
            See [RFC 4112](https://tools.ietf.org/html/rfc4122)

    Returns:
        Response[StreamsTypesStreamsModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
