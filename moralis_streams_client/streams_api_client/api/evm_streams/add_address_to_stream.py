from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...models.addresses_types_address_response import (
    AddressesTypesAddressResponse,
)
from ...models.addresses_types_addresses_add import AddressesTypesAddressesAdd
from ...types import UNSET, Response


def _get_kwargs(
    id: str,
    *,
    client: AuthenticatedClient,
    json_body: AddressesTypesAddressesAdd,
) -> Dict[str, Any]:
    url = "{}/streams/evm/{id}/address".format(client.base_url, id=id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[AddressesTypesAddressResponse]:
    if response.status_code == 200:
        response_200 = AddressesTypesAddressResponse.from_dict(response.json())

        return response_200
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[AddressesTypesAddressResponse]:
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
    json_body: AddressesTypesAddressesAdd,
) -> Response[AddressesTypesAddressResponse]:
    """Adds an address to a Stream.

    Args:
        id (str): Stringified UUIDv4.
            See [RFC 4112](https://tools.ietf.org/html/rfc4122)
        json_body (AddressesTypesAddressesAdd):

    Returns:
        Response[AddressesTypesAddressResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        client=client,
        json_body=json_body,
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
    json_body: AddressesTypesAddressesAdd,
) -> Optional[AddressesTypesAddressResponse]:
    """Adds an address to a Stream.

    Args:
        id (str): Stringified UUIDv4.
            See [RFC 4112](https://tools.ietf.org/html/rfc4122)
        json_body (AddressesTypesAddressesAdd):

    Returns:
        Response[AddressesTypesAddressResponse]
    """

    return sync_detailed(
        id=id,
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    json_body: AddressesTypesAddressesAdd,
) -> Response[AddressesTypesAddressResponse]:
    """Adds an address to a Stream.

    Args:
        id (str): Stringified UUIDv4.
            See [RFC 4112](https://tools.ietf.org/html/rfc4122)
        json_body (AddressesTypesAddressesAdd):

    Returns:
        Response[AddressesTypesAddressResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    json_body: AddressesTypesAddressesAdd,
) -> Optional[AddressesTypesAddressResponse]:
    """Adds an address to a Stream.

    Args:
        id (str): Stringified UUIDv4.
            See [RFC 4112](https://tools.ietf.org/html/rfc4122)
        json_body (AddressesTypesAddressesAdd):

    Returns:
        Response[AddressesTypesAddressResponse]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            json_body=json_body,
        )
    ).parsed
