from typing import Any, BinaryIO, Dict, Optional, TextIO, Tuple, Type, TypeVar

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Block")


@attr.s(auto_attribs=True)
class Block:
    """
    Attributes:
        number (str):
        hash_ (str):
        timestamp (str):
    """

    number: str
    hash_: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        number = self.number
        hash_ = self.hash_
        timestamp = self.timestamp

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "number": number,
                "hash": hash_,
                "timestamp": timestamp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        number = d.pop("number")

        hash_ = d.pop("hash")

        timestamp = d.pop("timestamp")

        block = cls(
            number=number,
            hash_=hash_,
            timestamp=timestamp,
        )

        return block
