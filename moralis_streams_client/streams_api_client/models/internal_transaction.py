from typing import Any, BinaryIO, Dict, Optional, TextIO, Tuple, Type, TypeVar

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="InternalTransaction")


@attr.s(auto_attribs=True)
class InternalTransaction:
    """
    Attributes:
        transaction_hash (str):
        stream_id (str):
        tag (str):
        stream_type (str):
        from_ (Optional[str]):
        to (Optional[str]):
        value (Optional[str]):
        gas (Optional[str]):
    """

    transaction_hash: str
    stream_id: str
    tag: str
    stream_type: str
    from_: Optional[str]
    to: Optional[str]
    value: Optional[str]
    gas: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        transaction_hash = self.transaction_hash
        stream_id = self.stream_id
        tag = self.tag
        stream_type = self.stream_type
        from_ = self.from_
        to = self.to
        value = self.value
        gas = self.gas

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "transactionHash": transaction_hash,
                "streamId": stream_id,
                "tag": tag,
                "streamType": stream_type,
                "from": from_,
                "to": to,
                "value": value,
                "gas": gas,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        transaction_hash = d.pop("transactionHash")

        stream_id = d.pop("streamId")

        tag = d.pop("tag")

        stream_type = d.pop("streamType")

        from_ = d.pop("from")

        to = d.pop("to")

        value = d.pop("value")

        gas = d.pop("gas")

        internal_transaction = cls(
            transaction_hash=transaction_hash,
            stream_id=stream_id,
            tag=tag,
            stream_type=stream_type,
            from_=from_,
            to=to,
            value=value,
            gas=gas,
        )

        return internal_transaction
