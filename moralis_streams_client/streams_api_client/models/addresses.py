from typing import Any, BinaryIO, Dict, Optional, TextIO, Tuple, Type, TypeVar

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Addresses")


@attr.s(auto_attribs=True)
class Addresses:
    """
    Attributes:
        address (str): Address
        id (str): Stringified UUIDv4.
            See [RFC 4112](https://tools.ietf.org/html/rfc4122)
    """

    address: str
    id: str

    def to_dict(self) -> Dict[str, Any]:
        address = self.address
        id = self.id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "address": address,
                "id": id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        address = d.pop("address")

        id = d.pop("id")

        addresses = cls(
            address=address,
            id=id,
        )

        return addresses
