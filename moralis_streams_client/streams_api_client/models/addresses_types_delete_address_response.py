from typing import Any, BinaryIO, Dict, Optional, TextIO, Tuple, Type, TypeVar

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="AddressesTypesDeleteAddressResponse")


@attr.s(auto_attribs=True)
class AddressesTypesDeleteAddressResponse:
    """
    Attributes:
        stream_id (str): The streamId
        address (str): Address
    """

    stream_id: str
    address: str

    def to_dict(self) -> Dict[str, Any]:
        stream_id = self.stream_id
        address = self.address

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "streamId": stream_id,
                "address": address,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        stream_id = d.pop("streamId")

        address = d.pop("address")

        addresses_types_delete_address_response = cls(
            stream_id=stream_id,
            address=address,
        )

        return addresses_types_delete_address_response
