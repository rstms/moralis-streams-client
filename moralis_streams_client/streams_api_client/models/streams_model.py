from typing import (
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

import attr

from ..models.streams_abi import StreamsAbi
from ..models.streams_filter import StreamsFilter
from ..models.streams_status import StreamsStatus
from ..models.streams_type import StreamsType
from ..types import UNSET, Unset

T = TypeVar("T", bound="StreamsModel")


@attr.s(auto_attribs=True)
class StreamsModel:
    """
    Attributes:
        webhook_url (str): Webhook URL where moralis will send the POST request.
        description (str): A description for this stream
        tag (str): A user-provided tag that will be send along the webhook, the user can use this tag to identify the
            specific stream if multiple streams are present
        chain_ids (List[str]): The ids of the chains for this stream in hex Ex: ["0x1","0x38"]
        type (StreamsType): The stream type:
            [wallet] listen to all native transactions of the address and all logs where the address is involved in at least
            one of the topics
            [contract] listens to all native transactions of the address and all logs produced by the contract address
        token_address (Union[Unset, None, str]): The token address of the contract, required if the type : log
        topic0 (Union[Unset, None, str]): The topic0 of the event in hex, required if the type : log
        include_native_txs (Union[Unset, bool]): Include or not native transactions defaults to false (only applied when
            type:contract)
        abi (Union[Unset, None, StreamsAbi]): The abi to parse the log object of the contract
        filter_ (Union[Unset, None, StreamsFilter]): The filter object, optional and only used if the type : log
            https://v1docs.moralis.io/moralis-dapp/automatic-transaction-sync/smart-contract-events#event-filters
        address (Union[Unset, None, str]): The wallet address of the user, required if the type : tx
        id (Union[Unset, str]): Stringified UUIDv4.
            See [RFC 4112](https://tools.ietf.org/html/rfc4122)
        status (Union[Unset, StreamsStatus]): The stream status:
            [active] The Stream is healthy and processing blocks
            [paused] The Stream is paused and is not processing blocks
            [error] The Stream has encountered an error and is not processing blocks
        status_message (Union[Unset, str]): Description of current status of stream.
    """

    webhook_url: str
    description: str
    tag: str
    chain_ids: List[str]
    type: StreamsType
    token_address: Union[Unset, None, str] = UNSET
    topic0: Union[Unset, None, str] = UNSET
    include_native_txs: Union[Unset, bool] = UNSET
    abi: Union[Unset, None, StreamsAbi] = UNSET
    filter_: Union[Unset, None, StreamsFilter] = UNSET
    address: Union[Unset, None, str] = UNSET
    id: Union[Unset, str] = UNSET
    status: Union[Unset, StreamsStatus] = UNSET
    status_message: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        webhook_url = self.webhook_url
        description = self.description
        tag = self.tag
        chain_ids = self.chain_ids

        type = self.type.value

        token_address = self.token_address
        topic0 = self.topic0
        include_native_txs = self.include_native_txs
        abi: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.abi, Unset):
            abi = self.abi.to_dict() if self.abi else None

        filter_: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.filter_, Unset):
            filter_ = self.filter_.to_dict() if self.filter_ else None

        address = self.address
        id = self.id
        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        status_message = self.status_message

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "webhookUrl": webhook_url,
                "description": description,
                "tag": tag,
                "chainIds": chain_ids,
                "type": type,
            }
        )
        if token_address is not UNSET:
            field_dict["tokenAddress"] = token_address
        if topic0 is not UNSET:
            field_dict["topic0"] = topic0
        if include_native_txs is not UNSET:
            field_dict["includeNativeTxs"] = include_native_txs
        if abi is not UNSET:
            field_dict["abi"] = abi
        if filter_ is not UNSET:
            field_dict["filter"] = filter_
        if address is not UNSET:
            field_dict["address"] = address
        if id is not UNSET:
            field_dict["id"] = id
        if status is not UNSET:
            field_dict["status"] = status
        if status_message is not UNSET:
            field_dict["statusMessage"] = status_message

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        webhook_url = d.pop("webhookUrl")

        description = d.pop("description")

        tag = d.pop("tag")

        chain_ids = cast(List[str], d.pop("chainIds"))

        type = StreamsType(d.pop("type"))

        token_address = d.pop("tokenAddress", UNSET)

        topic0 = d.pop("topic0", UNSET)

        include_native_txs = d.pop("includeNativeTxs", UNSET)

        _abi = d.pop("abi", UNSET)
        abi: Union[Unset, None, StreamsAbi]
        if _abi is None:
            abi = None
        elif isinstance(_abi, Unset):
            abi = UNSET
        else:
            abi = StreamsAbi.from_dict(_abi)

        _filter_ = d.pop("filter", UNSET)
        filter_: Union[Unset, None, StreamsFilter]
        if _filter_ is None:
            filter_ = None
        elif isinstance(_filter_, Unset):
            filter_ = UNSET
        else:
            filter_ = StreamsFilter.from_dict(_filter_)

        address = d.pop("address", UNSET)

        id = d.pop("id", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, StreamsStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = StreamsStatus(_status)

        status_message = d.pop("statusMessage", UNSET)

        streams_model = cls(
            webhook_url=webhook_url,
            description=description,
            tag=tag,
            chain_ids=chain_ids,
            type=type,
            token_address=token_address,
            topic0=topic0,
            include_native_txs=include_native_txs,
            abi=abi,
            filter_=filter_,
            address=address,
            id=id,
            status=status,
            status_message=status_message,
        )

        return streams_model
