# streams api client wrapper

import json
from typing import List

import moralis_streams_api as streams

from moralis_streams_client.defaults import MORALIS_STREAMS_URL


class MoralisStreamsApi:
    def __init__(self, api_key, url=MORALIS_STREAMS_URL, verbose=False):
        if not api_key:
            raise ValueError(f"{api_key=}")
        config = streams.Configuration()
        config.api_key["x-api-key"] = api_key
        config.host = url
        self.client = streams.ApiClient(config)
        self.verbose = verbose

    def _parse_advanced_options(self, advanced_options):
        options = []
        for option in advanced_options:
            odict = json.loads(option)
            options.append(
                streams.AdvancedOptions(
                    topic0=odict["topic0"],
                    filter=odict["filter"],
                    include_native_txs=odict["include_native_txs"],
                )
            )
        return options

    def get_stats(self) -> streams.StatstypesStatsModel:
        return streams.BetaApi(self.client).get_stats()

    def get_settings(self) -> streams.SettingsTypesSettingsModel:
        return streams.ProjectApi(self.client).get_settings()

    def set_settings(self, region: str) -> None:
        settings = streams.SettingsTypesSettingsModel(region=region)
        return streams.ProjectApi(self.client).set_settings(settings=settings)

    def create_stream(
        self,
        webhook_url: str,
        description: str,
        tag: str,
        topic0: str,
        all_addresses: bool,
        include_native_txs: bool,
        include_contract_logs: bool,
        include_internal_txs: bool,
        abi: List[str],
        advanced_options: List[str],
        chain_ids: List[str],
    ) -> streams.StreamsTypesStreamsModel:
        body = streams.StreamsTypesStreamsModelCreate(
            webhook_url=webhook_url,
            description=description,
            tag=tag,
            topic0=topic0,
            all_addresses=all_addresses,
            include_native_txs=include_native_txs,
            include_contract_logs=include_contract_logs,
            include_internal_txs=include_internal_txs,
            abi=abi,
            advanced_options=self._parse_advanced_options(advanced_options),
            chain_ids=chain_ids,
        )
        return streams.EvmStreamsApi(self.client).create_stream(body=body)

    def add_address_to_stream(
        self, stream_id: str, address_list: List[str]
    ) -> streams.AddressesTypesAddressResponse:
        id = streams.StreamsTypesUUID(stream_id)
        body = streams.AddressesTypesAddressesAdd(address=address_list)
        return streams.EvmStreamsApi(self.client).add_address_to_stream(
            body=body, id=id
        )

    def delete_address_from_stream(
        self, stream_id: str, address_list: List[str]
    ) -> streams.AddressesTypesDeleteAddressResponse:
        id = streams.StreamsTypesUUID(stream_id)
        body = streams.AddressesTypesAddressesRemove(address=address_list)
        return streams.EvmStreamsApi(self.client).delete_address_from_stream(
            body=body, id=id
        )

    def delete_stream(
        self, stream_id: str
    ) -> streams.StreamsTypesStreamsModel:
        id = streams.StreamsTypesUUID(stream_id)
        return streams.EvmStreamsApi(self.client).delete_stream(id=id)

    def get_addresses(
        self, stream_id: str, limit: float, cursor: str
    ) -> streams.AddressesTypesAddressResponse:
        id = streams.StreamsTypesUUID(stream_id)
        return streams.EvmStreamsApi(self.client).get_addessses(
            id=id, limit=limit, cursor=cursor
        )

    def get_stream(self, stream_id: str) -> streams.StreamsTypesStreamsModel:
        id = streams.StreamsTypesUUID(stream_id)
        return streams.EvmStreamsApi(self.client).get_stream(id=id)

    def get_streams(
        self, limit: float, cursor: str
    ) -> streams.StreamsTypesStreamsResponse:
        return streams.EvmStreamsApi(self.client).get_streams(
            limit=limit, cursor=cursor
        )

    def update_stream(
        self,
        stream_id: str,
        webhook_url: str = None,
        description: str = None,
        tag: str = None,
        topic0: str = None,
        all_addresses: bool = None,
        include_native_txs: bool = None,
        include_contract_logs: bool = None,
        include_internal_txs: bool = None,
        abi: List[str] = None,
        advanced_options: List[str] = None,
        chain_ids: List[str] = None,
    ) -> streams.StreamsTypesStreamsModel:
        id = streams.StreamsTypesUUID(stream_id)
        body = streams.streams.PartialStreamsTypesStreamsModelCreate_(
            webhook_url=webhook_url,
            description=description,
            tag=tag,
            topic0=topic0,
            all_addresses=all_addresses,
            include_native_txs=include_native_txs,
            include_contract_logs=include_contract_logs,
            include_internal_txs=include_internal_txs,
            abi=abi,
            advanced_options=self._parse_advanced_options(advanced_options),
            chain_ids=chain_ids,
        )
        return streams.EvmStreamsApi(self.client).update_stream(
            body=body, id=id
        )

    def update_stream_status(
        self, stream_id: str, status: str
    ) -> streams.StreamsTypesStreamsModel:
        id = streams.StreamsTypesUUID(stream_id)
        body = streams.StreamsTypesStreamsStatusUpdate(status)
        return streams.EvmStreamsApi(self.client).update_stream_status(
            body, id
        )

    def get_history(
        self, limit: float, cursor: str, exclude_payload: bool
    ) -> streams.HistoryTypesHistoryResponse:
        return streams.HistoryApi(self.client).get_history(
            limit=limit, cursor=cursor, exclude_payload=exclude_payload
        )

    def replay_history(self, id: str) -> streams.HistoryTypesHistoryModel:
        id = streams.HistoryTypesUUID(id)
        return streams.HistoryApi(self.client).replay_history(id=id)
