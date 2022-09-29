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

from ..types import UNSET, Unset

T = TypeVar("T", bound="AddressesTypesAddressResponse")


@attr.s(auto_attribs=True)
class AddressesTypesAddressResponse:
    """
    Attributes:
        stream_id (str): The streamId
        address (Union[List[str], str]): Address
    """

    stream_id: str
    address: Union[List[str], str]

    def to_dict(self) -> Dict[str, Any]:
        stream_id = self.stream_id
        address: Union[List[str], str]

        if isinstance(self.address, list):
            address = self.address

        else:
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

        def _parse_address(data: object) -> Union[List[str], str]:
            try:
                if not isinstance(data, list):
                    raise TypeError()
                address_type_1 = cast(List[str], data)

                return address_type_1
            except:  # noqa: E722
                pass
            return cast(Union[List[str], str], data)

        address = _parse_address(d.pop("address"))

        addresses_types_address_response = cls(
            stream_id=stream_id,
            address=address,
        )

        return addresses_types_address_response
