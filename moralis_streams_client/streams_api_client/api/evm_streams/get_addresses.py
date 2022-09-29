from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...models.addresses_types_addresses_response import (
    AddressesTypesAddressesResponse,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    client: AuthenticatedClient,
    limit: float,
    cursor: Union[Unset, None, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/streams/evm/{id}/address".format(client.base_url, id=id)

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
) -> Optional[AddressesTypesAddressesResponse]:
    if response.status_code == 200:
        response_200 = AddressesTypesAddressesResponse.from_dict(
            response.json()
        )

        return response_200
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[AddressesTypesAddressesResponse]:
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
    limit: float,
    cursor: Union[Unset, None, str] = UNSET,
) -> Response[AddressesTypesAddressesResponse]:
    """Get all addresses associated with a specific stream.

    Args:
        id (str): Stringified UUIDv4.
            See [RFC 4112](https://tools.ietf.org/html/rfc4122)
        limit (float):
        cursor (Union[Unset, None, str]):

    Returns:
        Response[AddressesTypesAddressesResponse]
    """

    kwargs = _get_kwargs(
        id=id,
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
    id: str,
    *,
    client: AuthenticatedClient,
    limit: float,
    cursor: Union[Unset, None, str] = UNSET,
) -> Optional[AddressesTypesAddressesResponse]:
    """Get all addresses associated with a specific stream.

    Args:
        id (str): Stringified UUIDv4.
            See [RFC 4112](https://tools.ietf.org/html/rfc4122)
        limit (float):
        cursor (Union[Unset, None, str]):

    Returns:
        Response[AddressesTypesAddressesResponse]
    """

    return sync_detailed(
        id=id,
        client=client,
        limit=limit,
        cursor=cursor,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    limit: float,
    cursor: Union[Unset, None, str] = UNSET,
) -> Response[AddressesTypesAddressesResponse]:
    """Get all addresses associated with a specific stream.

    Args:
        id (str): Stringified UUIDv4.
            See [RFC 4112](https://tools.ietf.org/html/rfc4122)
        limit (float):
        cursor (Union[Unset, None, str]):

    Returns:
        Response[AddressesTypesAddressesResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        client=client,
        limit=limit,
        cursor=cursor,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    limit: float,
    cursor: Union[Unset, None, str] = UNSET,
) -> Optional[AddressesTypesAddressesResponse]:
    """Get all addresses associated with a specific stream.

    Args:
        id (str): Stringified UUIDv4.
            See [RFC 4112](https://tools.ietf.org/html/rfc4122)
        limit (float):
        cursor (Union[Unset, None, str]):

    Returns:
        Response[AddressesTypesAddressesResponse]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            limit=limit,
            cursor=cursor,
        )
    ).parsed
