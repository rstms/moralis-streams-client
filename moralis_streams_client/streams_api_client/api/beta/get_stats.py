from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...models.stats_types_stats_model import StatsTypesStatsModel
from ...types import UNSET, Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/beta/stats".format(client.base_url)

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
) -> Optional[StatsTypesStatsModel]:
    if response.status_code == 200:
        response_200 = StatsTypesStatsModel.from_dict(response.json())

        return response_200
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[StatsTypesStatsModel]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[StatsTypesStatsModel]:
    """Get the stats for the current project based on the project api-key (Beta - This endpoint could be
    replaced or removed).

    Returns:
        Response[StatsTypesStatsModel]
    """

    kwargs = _get_kwargs(
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> Optional[StatsTypesStatsModel]:
    """Get the stats for the current project based on the project api-key (Beta - This endpoint could be
    replaced or removed).

    Returns:
        Response[StatsTypesStatsModel]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[StatsTypesStatsModel]:
    """Get the stats for the current project based on the project api-key (Beta - This endpoint could be
    replaced or removed).

    Returns:
        Response[StatsTypesStatsModel]
    """

    kwargs = _get_kwargs(
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Optional[StatsTypesStatsModel]:
    """Get the stats for the current project based on the project api-key (Beta - This endpoint could be
    replaced or removed).

    Returns:
        Response[StatsTypesStatsModel]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
