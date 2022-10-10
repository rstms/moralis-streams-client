# streams api client wrapper

import json
import logging
import os
from pprint import pformat
from typing import Dict, List

import requests
from eth_hash.auto import keccak
from eth_utils import to_hex
from requests.exceptions import HTTPError, JSONDecodeError

from .defaults import (
    ACTIVE,
    ERROR,
    PAGE_LIMIT,
    PAUSED,
    REGION,
    REGION_CHOICES,
    ROW_LIMIT,
    STREAMS_URL,
)

logger = logging.getLogger(__name__)
info = logger.info
debug = logger.debug


class MoralisStreamsError(Exception):
    pass


class ErrorReturned(MoralisStreamsError):
    pass


class CallFailed(MoralisStreamsError):
    pass


class ResponseFormatError(MoralisStreamsError):
    pass


class MoralisStreamsApi:
    def __init__(
        self,
        *,
        api_key=None,
        url=STREAMS_URL,
        region=REGION,
        debug=False,
        row_limit=ROW_LIMIT,
        page_limit=PAGE_LIMIT,
    ):
        self.api_key = api_key or os.environ["MORALIS_API_KEY"]
        self.url = url
        self.headers = {"x-api-key": api_key}
        self.page_limit = page_limit
        self.row_limit = row_limit
        self._init_region(region)
        self.debug = debug

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.__class__.__name__}<{hex(id(self))}>"

    def _init_region(self, region):
        self.get_settings()
        if self.region != region:
            self.set_settings(region=region)

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

    def _get(self, path, *, params={}, paginated=False, require_keys=[]):

        if paginated:
            return self._get_paginated(path, params)

        response = requests.get(
            self.url + path, headers=self.headers, params=params
        )
        return self._return_result(response, require_keys)

    def _post(self, path, body={}):
        response = requests.post(
            self.url + path, headers=self.headers, json=body
        )
        return self._return_result(response)

    def _put(self, path, body={}):
        response = requests.put(
            self.url + path, headers=self.headers, json=body
        )
        return self._return_result(response)

    def _delete(self, path, body={}):
        response = requests.delete(
            self.url + path, headers=self.headers, json=body
        )
        return self._return_result(response)

    def _return_result(self, response, require_keys=[]):
        try:
            response.raise_for_status()
        except HTTPError as exc:
            raise CallFailed(f"{exc}") from exc
        else:
            try:
                ret = response.json()
            except JSONDecodeError:
                raise ResponseFormatError(
                    f"expected JSON, got {response.text()}"
                )

        for key in require_keys:
            if key not in ret:
                raise CallFailed(f"missing '{key}' in {ret=}")

        return ret

    def _get_page(self, count, path, params, results, require_keys):

        debug("----")
        debug(f"{count=}")
        debug(f"get({repr(path)},{params=})")

        ret = self._get(path, params=params, require_keys=require_keys)

        debug(f"ret.keys={list(ret.keys())}")
        debug(f"ret.total={ret['total']}")
        debug(f"ret.cursor={ret.get('cursor', '<NOT_PRESENT>')}")
        result = ret.get("result")
        for i, r in enumerate(result):
            debug(f"  result[{i}]: {r['id']}")

        len_before = len(results)

        results.extend(result)

        len_after = len(results)
        debug(f"results extended from {len_before} to {len_after}")
        for i, r in enumerate(results):
            debug(f"  results[{i}]: {r['id']}")

        return ret, results

    def _get_paginated(self, path, params={}):
        results = []
        params.setdefault("limit", self.row_limit)
        ret = dict(cursor=None)
        count = 0
        while "cursor" in ret:
            params["cursor"] = ret["cursor"]

            ret, results = self._get_page(
                count, path, params, results, ["total", "result"]
            )

            # check for total overrun
            total = int(ret["total"])
            if len(results) > total:
                raise CallFailed(
                    f"overrun: {total=} results_len={len(results)}"
                )

            # check for runaway page count
            count += 1
            if count > self.page_limit:
                raise CallFailed(
                    f"exceeded page count limit ({self.page_limit})"
                )

        return results

    def get_stats(self) -> dict:
        debug(f"{self} get_stats()")
        ret = self._get("/beta/stats")
        debug(f"{self} {ret=}")
        return ret

    def get_settings(self) -> dict:
        debug(f"{self} get_settings()")
        settings = self._get("/settings", require_keys=["region"])
        self.region = settings["region"]
        ret = None
        debug(f"{self} {ret=}")
        return ret

    def set_settings(self, region: str) -> None:
        debug(f"{self} set_settings({region=})")
        self._post("/settings", dict(region=region))
        self.region = region
        ret = None
        debug(f"{self} {ret=}")
        return ret

    def create_stream(
        self,
        *,
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
        debug(f"{self} create_stream({params=})")
        ret = self._put("/streams/evm", params)
        debug(f"{self} {ret=}")
        return ret

    def add_address_to_stream(self, stream_id: str, address: str) -> dict:
        debug(f"{self} add_address_to_stream({stream_id=}, {address=})")
        path = f"/streams/evm/{stream_id}/address"
        params = dict(address=address)
        ret = self._post(path, params)
        debug(f"{self} {ret=}")
        return ret

    def delete_address_from_stream(self, stream_id: str, address: str) -> dict:
        debug(f"{self} delete_address_from_stream({stream_id=}, {address=})")
        path = f"/streams/evm/{stream_id}/address"
        params = dict(address=address)
        ret = self._delete(path, params)
        debug(f"{self} {ret=}")
        return ret

    def delete_stream(self, stream_id: str) -> dict:
        debug(f"{self} delete_stream({stream_id=})")
        path = f"/streams/evm/{stream_id}"
        ret = self._delete(path)
        debug(f"{self} {ret=}")
        return ret

    def get_addresses(self, stream_id: str) -> List[str]:
        debug(f"{self} get_addresses({stream_id=})")
        path = f"/streams/evm/{stream_id}/address"
        ret = self._get(path, paginated=True)
        debug(f"{self} {ret=}")
        return ret

    def get_stream(self, stream_id: str) -> dict:
        debug(f"{self} get_stream({stream_id=})")
        path = f"/streams/evm/{stream_id}"
        ret = self._get(path)
        debug(f"{self} {ret=}")
        return ret

    def get_streams(self) -> List[Dict]:
        debug(f"{self} get_streams()")
        path = "/streams/evm"
        ret = self._get(path, paginated=True)
        debug(f"{self} {ret=}")
        return ret

    def update_stream(
        self,
        stream_id: str,
        *,
        webhook_url: str = None,
        description: str = None,
        tag: str = None,
        topic0: List[str] = None,
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
        debug(f"{self} update_stream({stream_id=}, {params=})")
        ret = self._post(path, params)
        debug(f"{self} {ret=}")
        return ret

    def update_stream_status(self, stream_id: str, status: str) -> dict:
        debug(f"{self} update_stream_status({stream_id=}, {status=})")
        path = f"/streams/evm/{stream_id}/status"
        params = dict(status=status)
        ret = self._post(path, params)
        debug(f"{self} {ret=}")
        return ret

    def get_history(
        self,
        exclude_payload: bool = False,
    ) -> dict:
        debug(f"{self} get_history({exclude_payload=})")
        path = "/history"
        if exclude_payload is True:
            params = dict(excludePayload=exclude_payload)
        else:
            params = {}
        ret = self._get(path, params=params, paginated=True)
        debug(f"{self} {ret=}")
        return ret

    def replay_history(self, event_id: str) -> List[Dict]:
        debug(f"{self} replay_history({event_id=})")
        path = f"/history/replay/{event_id}"
        ret = self._post(path)
        debug(f"{self} {ret=}")
        return ret
