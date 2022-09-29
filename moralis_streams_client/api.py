# API object

from typing import Callable

import attr

from .streams_api_client import *

DEFAULT_API_URL = "https://api.moralis-streams.com"

# decorator to copy docstrings from api functions to class methods
def copy_doc(copy_func: Callable) -> Callable:
    """Use Example: copy_doc(self.copy_func)(self.func) or used as deco"""

    def wrapper(func: Callable) -> Callable:
        func.__doc__ = copy_func.__doc__
        return func

    return wrapper


@attr.s(auto_attribs=True)
class API:
    """API endpoints"""

    detailed: bool
    client: AuthenticatedClient

    def _call(self, parsed, detailed, kwargs):
        kwargs["client"] = self.client
        if self.detailed:
            return detailed(**kwargs)
        else:
            return parsed(**kwargs)

    async def _async_call(self, parsed, detailed, kwargs):
        kwargs["client"] = self.client
        if self.detailed:
            return await detailed(**kwargs)
        else:
            return await parsed(**kwargs)

    @copy_doc(_sp_get_stats)
    def get_stats(self, **kwargs):
        return self._call(_sp_get_stats, _sd_get_stats, kwargs)

    @copy_doc(_ap_get_stats)
    async def get_stats(self, **kwargs):
        return self._async_call(_ap_get_stats, _ad_get_stats, kwargs)


"""
    def get_history(self, **kwargs):
        return self._call(_sp_get_history, _sd_get_history, kwargs)

    async def get_history(self, **kwargs):
        return self._async_call(_ap_get_history, _ad_get_history, kwargs)

    def replay_history(self, **kwargs):
        return self._call(_sp_replay_history, _sd_replay_history, kwargs)

    async def replay_history(self, **kwargs):
        return self._async_call(_ap_replay_history, _ad_replay_history, kwargs)

    def get_settings(self, **kwargs):
        return self._call(_sp_get_settings, _sd_get_settings, kwargs)

    async def get_settings(self, **kwargs):
        return self._async_call(_ap_get_settings, _ad_get_settings, kwargs)

    def set_settings(self, **kwargs):
        return self._call(_sp_set_settings, _sd_set_settings, kwargs)

    async def set_settings(self, **kwargs):
        return self._async_call(_ap_set_settings, _ad_set_settings, kwargs)

    def add_address_to_stream(self, **kwargs):
        return self._call(
            _sp_add_address_to_stream, _sd_add_address_to_stream, kwargs
        )

    async def add_address_to_stream(self, **kwargs):
        return self._async_call(
            _ap_add_address_to_stream, _ad_add_address_to_stream, kwargs
        )

    def create_stream(self, **kwargs):
        return self._call(_sp_create_stream, _sd_create_stream, kwargs)

    async def create_stream(self, **kwargs):
        return self._async_call(_ap_create_stream, _ad_create_stream, kwargs)

    def delete_address_from_stream(self, **kwargs):
        return self._call(
            _sp_delete_address_from_stream,
            _sd_delete_address_from_stream,
            kwargs,
        )

    async def delete_address_from_stream(self, **kwargs):
        return self._async_call(
            _ap_delete_address_from_stream,
            _ad_delete_address_from_stream,
            kwargs,
        )

    def delete_stream(self, **kwargs):
        return self._call(_sp_delete_stream, _sd_delete_stream, kwargs)

    async def delete_stream(self, **kwargs):
        return self._async_call(_ap_delete_stream, _ad_delete_stream, kwargs)

    def get_addresses(self, **kwargs):
        return self._call(_sp_get_addresses, _sd_get_addresses, kwargs)

    async def get_addresses(self, **kwargs):
        return self._async_call(_ap_get_addresses, _ad_get_addresses, kwargs)

    def get_stream(self, **kwargs):
        return self._call(_sp_get_stream, _sd_get_stream, kwargs)

    async def get_stream(self, **kwargs):
        return self._async_call(_ap_get_stream, _ad_get_stream, kwargs)

    def get_streams(self, **kwargs):
        return self._call(_sp_get_streams, _sd_get_streams, kwargs)

    async def get_streams(self, **kwargs):
        return self._async_call(_ap_get_streams, _ad_get_streams, kwargs)

    def update_stream(self, **kwargs):
        return self._call(_sp_update_stream, _sd_update_stream, kwargs)

    async def update_stream(self, **kwargs):
        return self._async_call(_ap_update_stream, _ad_update_stream, kwargs)

    def update_streams(self, **kwargs):
        return self._call(_sp_update_streams, _sd_update_streams, kwargs)

    async def update_streams(self, **kwargs):
        return self._async_call(_ap_update_streams, _ad_update_streams, kwargs)
"""


def connect(
    *, key: str, url: str = DEFAULT_API_URL, detailed: bool = False
) -> API:
    client = AuthenticatedClient(
        base_url=self.url, token=self.key, auth_header_name="X-API-Key"
    )
    return API(client=client, detailed=detailed)
