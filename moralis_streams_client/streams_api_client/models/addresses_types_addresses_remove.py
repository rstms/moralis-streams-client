from typing import Any, BinaryIO, Dict, Optional, TextIO, Tuple, Type, TypeVar

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="AddressesTypesAddressesRemove")


@attr.s(auto_attribs=True)
class AddressesTypesAddressesRemove:
    """
    Attributes:
        address (str): The address to be removed from the Stream.
    """

    address: str

    def to_dict(self) -> Dict[str, Any]:
        address = self.address

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "address": address,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        address = d.pop("address")

        addresses_types_addresses_remove = cls(
            address=address,
        )

        return addresses_types_addresses_remove
