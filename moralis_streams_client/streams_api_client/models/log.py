from typing import Any, BinaryIO, Dict, Optional, TextIO, Tuple, Type, TypeVar

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Log")


@attr.s(auto_attribs=True)
class Log:
    """
    Attributes:
        tag (str):
        stream_id (str):
        stream_type (str):
        log_index (str):
        transaction_hash (str):
        address (str):
        data (str):
        topic0 (Optional[str]):
        topic1 (Optional[str]):
        topic2 (Optional[str]):
        topic3 (Optional[str]):
    """

    tag: str
    stream_id: str
    stream_type: str
    log_index: str
    transaction_hash: str
    address: str
    data: str
    topic0: Optional[str]
    topic1: Optional[str]
    topic2: Optional[str]
    topic3: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        tag = self.tag
        stream_id = self.stream_id
        stream_type = self.stream_type
        log_index = self.log_index
        transaction_hash = self.transaction_hash
        address = self.address
        data = self.data
        topic0 = self.topic0
        topic1 = self.topic1
        topic2 = self.topic2
        topic3 = self.topic3

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "tag": tag,
                "streamId": stream_id,
                "streamType": stream_type,
                "logIndex": log_index,
                "transactionHash": transaction_hash,
                "address": address,
                "data": data,
                "topic0": topic0,
                "topic1": topic1,
                "topic2": topic2,
                "topic3": topic3,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        tag = d.pop("tag")

        stream_id = d.pop("streamId")

        stream_type = d.pop("streamType")

        log_index = d.pop("logIndex")

        transaction_hash = d.pop("transactionHash")

        address = d.pop("address")

        data = d.pop("data")

        topic0 = d.pop("topic0")

        topic1 = d.pop("topic1")

        topic2 = d.pop("topic2")

        topic3 = d.pop("topic3")

        log = cls(
            tag=tag,
            stream_id=stream_id,
            stream_type=stream_type,
            log_index=log_index,
            transaction_hash=transaction_hash,
            address=address,
            data=data,
            topic0=topic0,
            topic1=topic1,
            topic2=topic2,
            topic3=topic3,
        )

        return log
