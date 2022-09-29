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

T = TypeVar("T", bound="AddressesTypesAddressesAdd")


@attr.s(auto_attribs=True)
class AddressesTypesAddressesAdd:
    """
    Attributes:
        address (Union[List[str], str]): The address or a list of addresses to be added to the Stream.
    """

    address: Union[List[str], str]

    def to_dict(self) -> Dict[str, Any]:
        address: Union[List[str], str]

        if isinstance(self.address, list):
            address = self.address

        else:
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

        addresses_types_addresses_add = cls(
            address=address,
        )

        return addresses_types_addresses_add
