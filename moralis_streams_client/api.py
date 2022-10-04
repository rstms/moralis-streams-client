# API object

from typing import Callable, List, Union

import attr

from .streams_api_client import (
    UNSET,
    AddressesTypesAddressesAdd,
    AddressesTypesAddressesRemove,
    AuthenticatedClient,
    PartialStreamsTypesStreamsModelCreate,
    Response,
    SettingsRegion,
    SettingsTypesSettingsModel,
    StreamsAbi,
    StreamsFilter,
    StreamsStatus,
    StreamsType,
    StreamsTypesStreamsModelCreate,
    StreamsTypesStreamsStatusUpdate,
    Unset,
    _ad_add_address_to_stream,
    _ad_create_stream,
    _ad_delete_address_from_stream,
    _ad_delete_stream,
    _ad_get_addresses,
    _ad_get_history,
    _ad_get_settings,
    _ad_get_stats,
    _ad_get_stream,
    _ad_get_streams,
    _ad_replay_history,
    _ad_set_settings,
    _ad_update_stream,
    _ad_update_stream_status,
    _ap_add_address_to_stream,
    _ap_create_stream,
    _ap_delete_address_from_stream,
    _ap_delete_stream,
    _ap_get_addresses,
    _ap_get_history,
    _ap_get_settings,
    _ap_get_stats,
    _ap_get_stream,
    _ap_get_streams,
    _ap_replay_history,
    _ap_set_settings,
    _ap_update_stream,
    _ap_update_stream_status,
    _sd_add_address_to_stream,
    _sd_create_stream,
    _sd_delete_address_from_stream,
    _sd_delete_stream,
    _sd_get_addresses,
    _sd_get_history,
    _sd_get_settings,
    _sd_get_stats,
    _sd_get_stream,
    _sd_get_streams,
    _sd_replay_history,
    _sd_set_settings,
    _sd_update_stream,
    _sd_update_stream_status,
    _sp_add_address_to_stream,
    _sp_create_stream,
    _sp_delete_address_from_stream,
    _sp_delete_stream,
    _sp_get_addresses,
    _sp_get_history,
    _sp_get_settings,
    _sp_get_stats,
    _sp_get_stream,
    _sp_get_streams,
    _sp_replay_history,
    _sp_set_settings,
    _sp_update_stream,
    _sp_update_stream_status,
)

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

    client: AuthenticatedClient
    detailed: bool
    format_dict: bool

    def _call(self, parsed, detailed, **kwargs):
        kwargs["client"] = self.client
        if self.detailed:
            return detailed(**kwargs)
        else:
            ret = parsed(**kwargs)
            if self.format_dict and hasattr(ret, "to_dict"):
                return ret.to_dict()
            else:
                return ret

    async def _async_call(self, parsed, detailed, **kwargs):
        kwargs["client"] = self.client
        if self.detailed:
            return await detailed(**kwargs)
        else:
            return await parsed(**kwargs)

    @copy_doc(_sp_get_stats)
    def get_stats(self):
        return self._call(_sp_get_stats, _sd_get_stats)

    @copy_doc(_sp_get_stats)
    async def async_get_stats(self):
        return self._async_call(_ap_get_stats, _ad_get_stats)

    @copy_doc(_sp_get_history)
    def get_history(
        self, *, limit: float, cursor: Union[Unset, None, str] = UNSET
    ):
        return self._call(
            _sp_get_history, _sd_get_history, limit=limit, cursor=cursor
        )

    @copy_doc(_sp_get_history)
    async def async_get_history(
        self, *, limit: float, cursor: Union[Unset, None, str] = UNSET
    ):
        return self._async_call(
            _ap_get_history, _ad_get_history, limit=limit, cursor=cursor
        )

    @copy_doc(_sp_replay_history)
    def replay_history(self, id: str):
        return self._call(_sp_replay_history, _sd_replay_history, id=id)

    @copy_doc(_sp_replay_history)
    async def async_replay_history(self, id: str):
        return self._async_call(_ap_replay_history, _ad_replay_history, id=id)

    @copy_doc(_sp_get_settings)
    def get_settings(self):
        return self._call(_sp_get_settings, _sd_get_settings)

    @copy_doc(_sp_get_settings)
    async def async_get_settings(self):
        return self._async_call(_ap_get_settings, _ad_get_settings)

    @copy_doc(_sp_set_settings)
    def set_settings(self, *, json_body: SettingsTypesSettingsModel):
        return self._call(
            _sp_set_settings, _sd_set_settings, json_body=json_body
        )

    @copy_doc(_sp_set_settings)
    async def async_set_settings(
        self, *, json_body: SettingsTypesSettingsModel
    ):
        return self._async_call(
            _ap_set_settings, _ad_set_settings, json_body=json_body
        )

    @copy_doc(_sp_add_address_to_stream)
    def add_address_to_stream(
        self, id: str, *, json_body: AddressesTypesAddressesAdd
    ):
        return self._call(
            _sp_add_address_to_stream,
            _sd_add_address_to_stream,
            id=id,
            json_body=json_body,
        )

    @copy_doc(_sp_add_address_to_stream)
    async def async_add_address_to_stream(
        self, id: str, *, json_body: AddressesTypesAddressesAdd
    ):
        return self._async_call(
            _ap_add_address_to_stream,
            _ad_add_address_to_stream,
            id=id,
            json_body=json_body,
        )

    @copy_doc(_sp_create_stream)
    def create_stream(
        self,
        *,
        webhook_url: str,
        description: str,
        tag: str,
        chain_ids: Union[str, List[str]],
        stream_type: StreamsType,
        address: str,
        topic: str = None,
        include_native_txs: bool = False,
        abi: dict = None,
        filter_: StreamsFilter = None,
    ):
        if isinstance(chain_ids, str):
            chain_ids = [chain_ids]
        if stream_type == StreamsType.CONTRACT:
            token_address = address
            address = None
        elif stream_type == StreamsType.WALLET:
            token_address = None
        else:
            raise ValueError(f"unexpected: {stream_type=}")

        return self._call(
            _sp_create_stream,
            _sd_create_stream,
            json_body=StreamsTypesStreamsModelCreate(
                webhook_url=webhook_url,
                description=description,
                tag=tag,
                chain_ids=chain_ids,
                type=stream_type,
                token_address=token_address,
                topic0=topic,
                include_native_txs=include_native_txs,
                abi=abi,
                filter_=filter_,
                address=address,
            ),
        )

    @copy_doc(_sp_create_stream)
    async def async_create_stream(
        self, *, json_body: StreamsTypesStreamsModelCreate
    ):
        return self._async_call(
            _ap_create_stream, _ad_create_stream, json_body=json_body
        )

    @copy_doc(_sp_delete_address_from_stream)
    def delete_address_from_stream(
        self, id: str, *, json_body: AddressesTypesAddressesRemove
    ):
        return self._call(
            _sp_delete_address_from_stream,
            _sd_delete_address_from_stream,
            id=id,
            json_body=json_body,
        )

    @copy_doc(_sp_delete_address_from_stream)
    async def async_delete_address_from_stream(
        self, id: str, *, json_body: AddressesTypesAddressesRemove
    ):
        return self._async_call(
            _ap_delete_address_from_stream,
            _ad_delete_address_from_stream,
            id=id,
            json_body=json_body,
        )

    @copy_doc(_sp_delete_stream)
    def delete_stream(self, id: str):
        return self._call(_sp_delete_stream, _sd_delete_stream, id=id)

    @copy_doc(_sp_delete_stream)
    async def async_delete_stream(self, id: str):
        return self._async_call(_ap_delete_stream, _ad_delete_stream, id=id)

    @copy_doc(_sp_get_addresses)
    def get_addresses(
        self, id: str, *, limit: float, cursor: Union[Unset, None, str] = UNSET
    ):
        return self._call(
            _sp_get_addresses,
            _sd_get_addresses,
            id=id,
            limit=limit,
            cursor=cursor,
        )

    @copy_doc(_sp_get_addresses)
    async def async_get_addresses(
        self, id: str, *, limit: float, cursor: Union[Unset, None, str] = UNSET
    ):
        return self._async_call(
            _ap_get_addresses,
            _ad_get_addresses,
            id=id,
            limit=limit,
            cursor=cursor,
        )

    @copy_doc(_sp_get_stream)
    def get_stream(self, id: str):
        return self._call(_sp_get_stream, _sd_get_stream, id=id)

    @copy_doc(_sp_get_stream)
    async def async_get_stream(self, id: str):
        return self._async_call(_ap_get_stream, _ad_get_stream, id=id)

    @copy_doc(_sp_get_streams)
    def get_streams(
        self,
        *,
        limit: float,
        cursor: Union[Unset, None, str] = UNSET,
    ):
        return self._call(
            _sp_get_streams, _sd_get_streams, limit=limit, cursor=cursor
        )

    @copy_doc(_sp_get_streams)
    async def async_get_streams(
        self,
        *,
        limit: float,
        cursor: Union[Unset, None, str] = UNSET,
    ):
        return self._async_call(
            _ap_get_streams, _ad_get_streams, limit=limit, cursor=cursor
        )

    @copy_doc(_sp_update_stream)
    def update_stream(
        self, id: str, *, json_body: PartialStreamsTypesStreamsModelCreate
    ):
        return self._call(
            _sp_update_stream, _sd_update_stream, id=id, json_body=json_body
        )

    @copy_doc(_sp_update_stream)
    async def async_update_stream(
        self, id: str, *, json_body: PartialStreamsTypesStreamsModelCreate
    ):
        return self._async_call(
            _ap_update_stream, _ad_update_stream, id=id, json_body=json_body
        )

    @copy_doc(_sp_update_stream_status)
    def update_stream_status(
        self, id: str, *, json_body: StreamsTypesStreamsStatusUpdate
    ):
        return self._call(
            _sp_update_stream_status,
            _sd_update_stream_status,
            id=id,
            json_body=json_body,
        )

    @copy_doc(_sp_update_stream_status)
    async def async_update_stream_status(
        self, id: str, *, json_body: StreamsTypesStreamsStatusUpdate
    ):
        return self._async_call(
            _ap_update_stream_status,
            _ad_update_stream_status,
            id=id,
            json_body=json_body,
        )


def connect(
    *,
    key: str,
    url: str = DEFAULT_API_URL,
    detailed: bool = False,
    format_dict=True,
) -> API:
    client = AuthenticatedClient(
        token=key, base_url=url, auth_header_name="x-api-key", prefix=None
    )
    return API(client=client, detailed=detailed, format_dict=format_dict)
