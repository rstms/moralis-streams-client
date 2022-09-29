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
from ..models.streams_type import StreamsType
from ..types import UNSET, Unset

T = TypeVar("T", bound="PartialStreamsTypesStreamsModelCreate")


@attr.s(auto_attribs=True)
class PartialStreamsTypesStreamsModelCreate:
    """Make all properties in T optional

    Attributes:
        webhook_url (Union[Unset, str]): Webhook URL where moralis will send the POST request.
        description (Union[Unset, str]): A description for this stream
        tag (Union[Unset, str]): A user-provided tag that will be send along the webhook, the user can use this tag to
            identify the specific stream if multiple streams are present
        token_address (Union[Unset, None, str]): The token address of the contract, required if the type : log
        topic0 (Union[Unset, None, str]): The topic0 of the event in hex, required if the type : log
        include_native_txs (Union[Unset, bool]): Include or not native transactions defaults to false (only applied when
            type:contract)
        abi (Union[Unset, None, StreamsAbi]): The abi to parse the log object of the contract
        filter_ (Union[Unset, None, StreamsFilter]): The filter object, optional and only used if the type : log
            https://v1docs.moralis.io/moralis-dapp/automatic-transaction-sync/smart-contract-events#event-filters
        address (Union[Unset, None, str]): The wallet address of the user, required if the type : tx
        chain_ids (Union[Unset, List[str]]): The ids of the chains for this stream in hex Ex: ["0x1","0x38"]
        type (Union[Unset, StreamsType]): The stream type:
            [wallet] listen to all native transactions of the address and all logs where the address is involved in at least
            one of the topics
            [contract] listens to all native transactions of the address and all logs produced by the contract address
    """

    webhook_url: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    tag: Union[Unset, str] = UNSET
    token_address: Union[Unset, None, str] = UNSET
    topic0: Union[Unset, None, str] = UNSET
    include_native_txs: Union[Unset, bool] = UNSET
    abi: Union[Unset, None, StreamsAbi] = UNSET
    filter_: Union[Unset, None, StreamsFilter] = UNSET
    address: Union[Unset, None, str] = UNSET
    chain_ids: Union[Unset, List[str]] = UNSET
    type: Union[Unset, StreamsType] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        webhook_url = self.webhook_url
        description = self.description
        tag = self.tag
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
        chain_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.chain_ids, Unset):
            chain_ids = self.chain_ids

        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if webhook_url is not UNSET:
            field_dict["webhookUrl"] = webhook_url
        if description is not UNSET:
            field_dict["description"] = description
        if tag is not UNSET:
            field_dict["tag"] = tag
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
        if chain_ids is not UNSET:
            field_dict["chainIds"] = chain_ids
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        webhook_url = d.pop("webhookUrl", UNSET)

        description = d.pop("description", UNSET)

        tag = d.pop("tag", UNSET)

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

        chain_ids = cast(List[str], d.pop("chainIds", UNSET))

        _type = d.pop("type", UNSET)
        type: Union[Unset, StreamsType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = StreamsType(_type)

        partial_streams_types_streams_model_create = cls(
            webhook_url=webhook_url,
            description=description,
            tag=tag,
            token_address=token_address,
            topic0=topic0,
            include_native_txs=include_native_txs,
            abi=abi,
            filter_=filter_,
            address=address,
            chain_ids=chain_ids,
            type=type,
        )

        partial_streams_types_streams_model_create.additional_properties = d
        return partial_streams_types_streams_model_create

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
