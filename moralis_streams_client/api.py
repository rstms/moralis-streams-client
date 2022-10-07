# streams api client wrapper

import json
from pprint import pformat
from typing import Dict, List

import requests

from .defaults import MORALIS_STREAMS_URL


class MoralisStreamsError(Exception):
    pass


class ErrorReturned(MoralisStreamsError):
    pass


class CallFailed(MoralisStreamsError):
    pass


REGIONS = ["us-east-1", "us-west-2", "eu-central-1", "ap-southeast-1"]

STREAM_STATUS = ["active", "paused", "error"]


class MoralisStreamsApi:
    def __init__(self, api_key, url=MORALIS_STREAMS_URL, verbose=False):
        if not api_key:
            raise ValueError(f"{api_key=}")
        self.url = url
        self.headers = {"x-api-key": api_key}
        self.verbose = verbose

    def _parse_advanced_options(self, advanced_options):
        options = advanced_options or []
        for o in options:
            odict = json.loads(o)
            options.append(
                {
                    key: odict[key]
                    for key in ["topic0", "filter", "includeNativeTxs"]
                }
            )
        return options

    def get(self, path, params=None):
        response = requests.get(
            self.url + path, headers=self.headers, params=params
        )
        return self.return_result(response)

    def post(self, path, body={}):
        response = requests.post(
            self.url + path, headers=self.headers, json=body
        )
        return self.return_result(response)

    def put(self, path, body={}):
        response = requests.put(
            self.url + path, headers=self.headers, json=body
        )
        return self.return_result(response)

    def delete(self, path, body={}):
        response = requests.delete(
            self.url + path, headers=self.headers, json=body
        )
        return self.return_result(response)

    def return_result(self, response):
        if not response.ok:
            try:
                msg = response.json()
            except Exception as exc:
                print(type(exc))
                breakpoint()
                raise CallFailed(response.text)
            raise ErrorReturned(pformat(msg))
        return response.json()

    def get_stats(self) -> dict:
        return self.get("/beta/stats")

    def get_settings(self) -> dict:
        return self.get("/project/settings")

    def set_settings(self, region: str) -> None:
        self.post("/project/settings", dict(region=region))

    def create_stream(
        self,
        webhook_url: str,
        description: str,
        tag: str,
        topic0: List[str],
        all_addresses: bool,
        include_native_txs: bool,
        include_contract_logs: bool,
        include_internal_txs: bool,
        abi: List[Dict],
        advanced_options: List[Dict],
        chain_ids: List[str],
    ) -> dict:

        params = dict(
            webhookUrl=webhook_url,
            description=description,
            tag=tag,
            topic0=topic0,
            allAddresses=all_addresses,
            includeNativeTxs=include_native_txs,
            includeContractLogs=include_contract_logs,
            includeInternalTxs=include_internal_txs,
            abi=abi,
            advancedOptions=self._parse_advanced_options(advanced_options),
            chainIds=chain_ids,
        )
        return self.put("/streams/evm", params)

    def add_address_to_stream(self, stream_id: str, address: str) -> dict:
        path = f"/streams/evm/{stream_id}/address"
        params = dict(address=address)
        return self.post(path, params)

    def delete_address_from_stream(self, stream_id: str, address: str) -> dict:
        path = f"/streams/evm/{stream_id}/address"
        params = dict(address=address)
        return self.delete(path, params)

    def delete_stream(self, stream_id: str) -> dict:
        path = f"/streams/evm/{stream_id}"
        return self.delete(path)

    def query_params(self, limit, cursor):
        params = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        return params

    def get_addresses(
        self, stream_id: str, limit: int = 100, cursor: str = None
    ) -> List[str]:
        path = f"/streams/evm/{stream_id}/address"
        params = self.query_params(limit, cursor)
        return self.get(path, params)

    def get_stream(self, stream_id: str) -> dict:
        path = f"/streams/evm/{stream_id}"
        return self.get(path)

    def get_streams(self, limit: int = 100, cursor: str = None) -> List[Dict]:
        path = "/streams/evm"
        params = self.query_params(limit, cursor)
        return self.get(path, params)

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
    ) -> dict:
        path = f"/streams/evm/{stream_id}"
        params = dict(
            webhookUrl=webhook_url,
            description=description,
            tag=tag,
            topic0=topic0,
            allAddresses=all_addresses,
            includeNativeTxs=include_native_txs,
            includeContractLogs=include_contract_logs,
            includeInternalTxs=include_internal_txs,
            abi=abi,
            advancedOptions=self._parse_advanced_options(advanced_options),
            chainIds=chain_ids,
        )
        return self.post(path, params)

    def update_stream_status(self, stream_id: str, status: str) -> dict:
        path = f"/streams/evm/{stream_id}/status"
        params = dict(status=status)
        return self.post(path, params)

    def get_history(
        self,
        limit: int = 100,
        cursor: str = None,
        exclude_payload: bool = False,
    ) -> dict:
        path = "/history"
        params = self.query_params(limit, cursor)
        params["exclude_payload"] = exclude_payload
        return self.get(path, params)

    def replay_history(self, event_id: str) -> List[Dict]:
        path = f"/history/replay/{event_id}"
        return self.post(path)
