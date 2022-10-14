# streams api client wrapper

import json
import logging
import os
from pprint import pformat
from typing import Dict, List

import requests
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
from .exceptions import (
    MoralisStreamsCallFailed,
    MoralisStreamsErrorReturned,
    MoralisStreamsResponseFormatError,
)

logger = logging.getLogger(__name__)
info = logger.info
debug = logger.debug
error = logging.error


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

    def kludge(self, message):
        """patch buggy return value seen on 2022-10-11 in POST streams/evm/{streamID}"""
        if "0" in message and "1" in message and message["0"] == "id":
            error('patching "0":"id", "1":"<stream_id>"')
            message[message.pop("0")] == message.pop("1")
        return message

    def _return_result(self, response, require_keys=[]):
        errors = []
        try:
            message = response.json()
        except JSONDecodeError as exc:
            message = response.text
            errors.append(MoralisStreamsResponseFormatError(f"{exc}"))

        message = self.kludge(message)

        try:
            response.raise_for_status()
        except HTTPError as exc:
            errors.append(str(exc))
            raise MoralisStreamsCallFailed((message, errors)) from exc

        if isinstance(message, dict):
            for key in require_keys:
                if key not in message:
                    errors.append(f"missing required key '{key}'")

        if errors:
            raise MoralisStreamsResponseFormatError((message, errors))

        if response.ok is False:
            raise MoralisStreamsErrorReturned((message, response.reason))

        return message

    def _get_page(self, count, path, params, results, require_keys):

        debug("----")
        debug(f"{count=}")
        debug(f"get({repr(path)},{params=})")

        ret = self._get(path, params=params, require_keys=require_keys)

        debug(f"ret.keys={list(ret.keys())}")
        debug(f"  total={ret['total']}")
        debug(f"  cursor={ret.get('cursor', '<NOT_PRESENT>')}")
        result = ret.get("result")
        debug(f"  result=[{len(result)}]")
        for i, r in enumerate(result):
            debug(f"    result[{i}]: {r['id']}")

        if len(result) > 0:
            len_before = len(results)
            results.extend(result)
            len_after = len(results)
            debug(f"results: [{len_before}] -> [{len_after}]")
            for i, r in enumerate(results):
                debug(f"  results[{i}]: {r['id']}")

        return ret, results

    def _get_paginated(self, path, params={}):
        results = []
        params.setdefault("limit", self.row_limit)
        count = 0
        cursor = None
        total = None
        debug("---BEGIN_PAGINATED---")
        while True:
            if cursor:
                params["cursor"] = cursor
            else:
                params.pop("cursor", None)

            ret, results = self._get_page(
                count, path, params, results, ["total", "result"]
            )

            _total = int(ret["total"])
            if total is None:
                total = _total
                debug(f"setting {total=} on iteration {count=}")
            else:
                if total != _total:
                    raise MoralisStreamsResponseFormatError(
                        f"total_changed: original={total=} latest={_total} {count=}"
                    )

            if len(results) == total:
                debug(f"pagination_exit: {total=} results={len(results)}")
                break

            # missing cursor exit
            try:
                cursor = ret["cursor"]
            except KeyError:
                debug("pagination_exit: no cursor in ret")
                break

            # null or empty string cursor exit
            if cursor in ["", None]:
                error(f"NULL cursor returned: NULL cursor={repr(cursor)}")

            # check for total overrun
            if len(results) > total:
                raise MoralisStreamsResponseFormatError(
                    f"overrun: {total=} results_len={len(results)}"
                )

            # check for runaway page count
            count += 1
            if count > self.page_limit:
                raise MoralisStreamsResponseFormatError(
                    f"exceeded page count limit ({self.page_limit})"
                )

        if total is None:
            raise MoralisStreamsResponseFormatError("exited with {total=}")

        if len(results) != total:
            raise MoralisStreamsResponseFormatError(
                f"results length mismatch: {total=} len(results)={len(results)}"
            )

        debug("---END_PAGINATED---")

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
