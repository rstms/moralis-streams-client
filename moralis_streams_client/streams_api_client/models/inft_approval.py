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
    cast,
)

import attr

from ..models.inft_approval_erc721 import INFTApprovalERC721
from ..models.inft_approval_erc1155 import INFTApprovalERC1155
from ..types import UNSET, Unset

T = TypeVar("T", bound="INFTApproval")


@attr.s(auto_attribs=True)
class INFTApproval:
    """
    Attributes:
        erc721 (List[INFTApprovalERC721]):
        erc1155 (List[INFTApprovalERC1155]):
    """

    erc721: List[INFTApprovalERC721]
    erc1155: List[INFTApprovalERC1155]

    def to_dict(self) -> Dict[str, Any]:
        erc721 = []
        for erc721_item_data in self.erc721:
            erc721_item = erc721_item_data.to_dict()

            erc721.append(erc721_item)

        erc1155 = []
        for erc1155_item_data in self.erc1155:
            erc1155_item = erc1155_item_data.to_dict()

            erc1155.append(erc1155_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "ERC721": erc721,
                "ERC1155": erc1155,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        erc721 = []
        _erc721 = d.pop("ERC721")
        for erc721_item_data in _erc721:
            erc721_item = INFTApprovalERC721.from_dict(erc721_item_data)

            erc721.append(erc721_item)

        erc1155 = []
        _erc1155 = d.pop("ERC1155")
        for erc1155_item_data in _erc1155:
            erc1155_item = INFTApprovalERC1155.from_dict(erc1155_item_data)

            erc1155.append(erc1155_item)

        inft_approval = cls(
            erc721=erc721,
            erc1155=erc1155,
        )

        return inft_approval
